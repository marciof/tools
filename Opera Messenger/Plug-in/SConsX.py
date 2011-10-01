# -*- coding: UTF-8 -*-


# Standard library:
from __future__ import division, print_function, unicode_literals
import atexit, os, re, shutil, subprocess, sys, tempfile

# External modules:
import SCons


def action(f):
    SCons.Script.AddMethod(SCons.Script.Environment, f)
    return f


def link_linux_library(env, name):
    full_name = env['LIBPREFIX'] + name + env['LIBSUFFIX']
    
    process = subprocess.Popen(['whereis', '-b', full_name],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    
    (output, errors) = process.communicate()
    
    if errors.strip() == '':
        paths = output.strip().split(' ')
        paths.pop(0)
        
        for path in paths:
            (library_dir, library) = os.path.split(path)
            
            if library == full_name:
                root = os.path.dirname(library_dir)
                
                env.Append(CPPPATH = [os.path.join(root, 'include')])
                env.Append(LIBPATH = [library_dir])
                env.Append(LIBS = [name])
                return
    
    env.Warning('Library not found:', name)


def link_windows_library(env, name, vendor):
    versions = []
    
    try:
        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\' + vendor)
        i = 0
        
        while True:
            subkey = _winreg.EnumKey(key, i)
            i += 1
            
            if subkey.startswith(name):
                versions.append(subkey)
    except WindowsError:
        pass
    
    if len(versions) == 0:
        env.Warning('Library not found:', name)
        return
    elif len(versions) == 1:
        [version] = versions
    else:
        versions.sort()
        version = versions.pop()
        env.Warning('Choosing newest library version:', version)
    
    path = _winreg.QueryValue(key, version)
    
    if env.BuildTool()[0] == 'MSVC':
        env.Append(CCFLAGS = ['/MD'])
    
    env.Append(CPPPATH = [os.path.join(path, 'include')])
    env.Append(LIBPATH = [os.path.join(path, 'lib')])
    env.Append(LIBS = [name])


@action
def BuildTool(env):
    """
    Gets the name of the currently selected build tool.
    """
    
    tools = env['TOOLS']
    color_gcc = 'colorgcc'
    
    # The order of each alias is significant.
    aliases = {
        'GNU': ['mingw', 'g++', 'gcc'],
        'MSVC': ['msvc'],
    }
    
    env['ENV'].update({
        'HOME': '',
        'TERM': os.environ['TERM'],
    })
    
    # TODO: Color support for Windows: http://code.google.com/p/colorconsole/
    if sys.stdout.isatty():
        if sys.platform == 'win32':
            (gray_color, no_color) = ('', '')
        else:
            (gray_color, no_color) = ('\033[0;37m', '\033[0m')
        
        for name in ['AS', 'CXX', 'LINK']:
            command = name + 'COM'
            
            if (command + 'STR') not in env:
                env[command + 'STR'] = '> %s$%s%s' \
                    % (gray_color, command, no_color),
    
    for (name, aliases) in aliases.items():
        for alias in aliases:
            if alias not in tools:
                continue
            
            if (name == 'GNU') and (env.WhereIs(color_gcc) is None):
                env.Warning('Won\'t color compiler output: "%s" not found.'
                    % color_gcc)
            
            return (name, alias)


@action
def CompileIDL(env, file):
    for path in env['ENV']['INCLUDE'].split(os.pathsep):
        source_file = os.path.join(path, file)
        
        if os.path.exists(source_file):
            env.Command(file, source_file, Copy('$TARGET', '$SOURCE'))
            env.TypeLibrary(file)
            break


# TODO: Override env.Program on Windows to automatically embed the manifest.
@action
def EmbedManifest(env, target):
    """
    Embeds the associated manifest file in the executable/library file itself.
    """
    
    (EXE_TYPE, DLL_TYPE) = (1, 2)
    
    file_type = EXE_TYPE if str(target).endswith('.exe') else DLL_TYPE
    manifest = '${TARGET}.manifest'
    output_rc = '-outputresource:$TARGET;%d' % file_type
    mt = env.Action([['mt', '-nologo', '-manifest', manifest, output_rc]])
    
    env.AddPostAction(target, mt)
    env.Clean(target, '%s.manifest' % target)


@action
def Files(env, pattern, root = os.curdir, recurse = False, variant = None):
    """
    Lists all files according to a given criteria.
    """
    
    patterns = pattern if isinstance(pattern, list) else [pattern]
    files = []
    
    for pattern in patterns:
        files.extend(env.Glob(os.path.join(root, pattern), strings = True))
    
    if variant is not None:
        files = [os.path.join(variant, f) for f in files]
    
    if recurse:
        if not callable(recurse):
            recurse = lambda path: True
        
        for name in os.listdir(root):
            path = os.path.normpath(os.path.join(root, name))
            
            if os.path.isdir(path) and recurse(path):
                files.extend(Files(env, patterns, path, recurse, variant))
    
    return files


@action
def LinkLibrary(env, name, vendor):
    """
    Finds and links with a given library.
    """
    
    config = env.Configure(log_file = tempfile.mkstemp()[1])
    found = config.CheckLib(name)
    config.Finish()
    
    if not found:
        try:
            import _winreg
            global _winreg
            link_windows_library(env, name, vendor)
        except ImportError:
            link_linux_library(env, name)


@action
def Warning(env, *message):
    print('Warning:', *message, file = sys.stderr)


if SCons.Script.GetOption('clean') or SCons.Script.GetOption('help'):
    def clean(*paths):
        for path in paths:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
    
    db_file = SCons.SConsign.DB_Name + SCons.dblite.dblite_suffix
    conf_dir = SCons.Defaults.ConstructionEnvironment['CONFIGUREDIR']
    
    atexit.register(clean, db_file, re.sub('^#/', '', conf_dir))
