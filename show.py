#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO: Simplify logic (e.g. Pager.run, encoding, etc), add documentation.
# TODO: Add option to disable coloring. Should it be automatic for large files?
# TODO: Automatic decoding of Base 64, quoted-printable, and encoded URI's?
# TODO: Don't display diff for removed files.
# TODO: Take line width and wrapping into account when paging.
# TODO: Follow file automatically if it changes size?
# TODO: Add support for data URI's? data:text/plain,www.example.com
# TODO: Clean up exception handling.
#       $ ./show.py -f file ^C ^C
#       $ ./show.py long-file ^C
# TODO: Do a text search if given a directory as the second file (e.g. ack-grep,
#       git-grep). Leverage grin? <http://pypi.python.org/pypi/grin>
#       $ ./show.py text .
#       $ ./show.py '\d+' ~
# TODO: Do a file search if given a directory as the fist file (e.g. find).
#       $ ./show.py . '*.txt'
# TODO: Convert to C++ for speed? Or re-use existing programs?
#       http://www.andre-simon.de/doku/highlight/en/highlight.html
#       http://www.gnu.org/software/src-highlite/


# Standard library:
from __future__ import unicode_literals
import abc, codecs, errno, locale, os, re, struct, subprocess, sys

# External modules:
import argparse, chardet, peak.util.imports, \
    pygments, pygments.formatters, pygments.lexers


filelike = peak.util.imports.lazyModule(b'filelike')
httplib = peak.util.imports.lazyModule(b'httplib')
urllib2 = peak.util.imports.lazyModule(b'urllib2')


class InputType (argparse.FileType):
    def __init__(self):
        super(InputType, self).__init__()
        self._password_manager = None
    
    
    def __call__(self, path):
        try:
            return super(InputType, self).__call__(path)
        except argparse.ArgumentTypeError as error:
            pass
        except IOError as error:
            if error.errno == errno.EISDIR:
                return self._list_directory(path)
            elif error.errno != errno.ENOENT:
                raise
        
        for url in [path, 'http://' + path]:
            try:
                return self._open_url(url)
            except (IOError, httplib.InvalidURL):
                pass
        
        try:
            return self._open_perldoc(path)
        except IOError:
            pass
        
        if path == 'self':
            return file(sys.argv[0])
        
        go_to_line = re.search(r'^ (.+?) : (\d+) $', path, re.VERBOSE)
        
        if go_to_line is not None:
            (path, line) = go_to_line.group(1, 2)
            try:
                return self._set_attrs_or_wrap(self.__call__(path),
                    line = int(line))
            except IOError:
                pass
        
        raise error
    
    
    def _list_directory(self, path):
        color = '--color=%s' % ('always' if sys.stdout.isatty() else 'auto')
        options = ['-CFXh', color, '--group-directories-first'] + sys.argv[1:]
        
        process = subprocess.Popen(
            args = ['ls'] + options,
            stdout = subprocess.PIPE)
        
        return self._set_attrs_or_wrap(process.stdout, name = path)
    
    
    def _open_perldoc(self, module):
        identifier = r'^[A-Z_a-z][0-9A-Z_a-z]*(?:::[0-9A-Z_a-z]+)*$'
        error_message = 'Not a Perl module: '
        process = None
        
        if not re.match(identifier, module):
            raise IOError(error_message + module)
        
        for implementation in ['perldoc', 'perldoc.bat']:
            try:
                process = subprocess.Popen([implementation, module],
                    stderr = file(os.devnull),
                    stdout = subprocess.PIPE)
                
                break
            except OSError as error:
                if error.errno != errno.ENOENT:
                    raise
        
        if process is None:
            raise IOError(str(OSError(errno.ENOENT)))
        
        if process.wait() == 0:
            return self._set_attrs_or_wrap(process.stdout, name = module)
        else:
            raise IOError(error_message + module)
    
    
    def _open_auth_url(self, url, error):
        if not sys.stdout.isatty():
            raise error
        
        if self._password_manager is None:
            self._password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        
        import getpass
        
        while True:
            password_manager = self._password_manager
            (user, password) = password_manager.find_user_password(
                None, url)
            
            if (user is None) and (password is None):
                print >> sys.stderr, str(error) + ': ' + url
                user = raw_input('User: ')
                password = getpass.getpass()
                password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_manager.add_password(None, url, user, password)
            
            handler = urllib2.HTTPBasicAuthHandler(password_manager)
            request = urllib2.Request(url)
            
            try:
                stream = urllib2.build_opener(handler).open(request)
            except urllib2.HTTPError as error:
                if error.code != httplib.UNAUTHORIZED:
                    raise
            else:
                stream.name = url
                self._password_manager.add_password(None, url, user, password)
                return stream
    
    
    def _open_url(self, url):
        try:
            return filelike.open(url)
        except IOError:
            pass
        
        try:
            return urllib2.urlopen(url)
        except urllib2.HTTPError as error:
            if error.code == httplib.UNAUTHORIZED:
                return self._open_auth_url(url, error)
            else:
                raise
        except ValueError as (error,):
            if error.startswith('unknown url type: '):
                raise httplib.InvalidURL(url)
            else:
                raise
    
    
    def _set_attrs_or_wrap(self, input, **kargs):
        try:
            for name, value in kargs.items():
                setattr(input, name, value)
            return input
        except (AttributeError, TypeError):
            return self._set_attrs_or_wrap(filelike.wrappers.FileWrapper(input),
                **kargs)


class ArgumentsParser (argparse.ArgumentParser):
    def __init__(self):
        super(ArgumentsParser, self).__init__(
            description = '''Automatic pager with syntax highlighting and diff
                support.''',
            epilog = '''An input can be '-' for standard input (default), a
                file path, an URL, a Perl module name, or 'self' for the
                source code. The input's name can also be suffixed with a colon
                followed by a line number to scroll to. If given a directory,
                its' contents are listed instead.''')
        
        self._input_type = InputType()
        
        arguments = [
            ('-f', {
                b'action': 'store_true',
                b'default': False,
                b'dest': 'follow',
                b'help': 'follow file like tail, and disable paging',
            }),
            ('-L', {
                b'action': 'append',
                b'dest': 'label',
                b'help': 'diff labels',
            }),
            ('-p', {
                b'action': 'store_true',
                b'default': False,
                b'dest': 'passthrough',
                b'help': 'passthrough mode, just page input',
            }),
            ('-t', {
                b'action': 'store_true',
                b'default': False,
                b'dest': 'terminal_only',
                b'help': 'use terminal only, no graphical interfaces',
            }),
            ('-u', {
                b'action': 'store_const',
                b'const': None,
                b'help': 'ignored for diff compatibility',
            }),
            ('input', {
                b'help': 'input to display, or Git diff file path',
                b'nargs': '?',
            }),
            ('input2', {
                b'help': 'input to compare with, or current Git file version',
                b'nargs': '?',
                b'type': self._input_type,
            }),
        ]
        
        git_arguments = [
            ('old_hex', {
                b'help': 'current Git file commit',
                b'nargs': '?',
            }),
            ('old_mode', {
                b'help': 'current Git file mode',
                b'nargs': '?',
            }),
            ('new_file', {
                b'help': 'working copy Git file version',
                b'nargs': '?',
                b'type': self._input_type,
            }),
            ('new_hex', {
                b'help': 'working copy Git file commit',
                b'nargs': '?',
            }),
            ('new_mode', {
                b'help': 'working copy Git file mode',
                b'nargs': '?',
            }),
        ]
        
        git_group = self.add_argument_group(
            title = 'Git external diff arguments')
        
        for (group, args) in [(self, arguments), (git_group, git_arguments)]:
            for name, options in args:
                group.add_argument(name, **options)
    
    
    def parse_args(self):
        args = super(ArgumentsParser, self).parse_args()
        return self._handle_arguments(args)
    
    
    def parse_known_args(self):
        (args, unknown_args) = super(ArgumentsParser, self).parse_known_args()
        return (self._handle_arguments(args, unknown_args), unknown_args)
    
    
    def _handle_arguments(self, args, unknown_args = []):
        if args.input is None:
            if sys.stdin.isatty() \
                    and (len(unknown_args) > 0 or len(sys.argv) == 1):
                args.input = os.path.curdir
            else:
                args.input = sys.stdin
        
        if args.new_file is not None:
            self._handle_git_diff_arguments(args)
        elif isinstance(args.input, basestring):
            if os.path.isdir(args.input):
                args.passthrough = True
            
            args.input = self._input_type(args.input)
        
        if args.input2 is None:
            args.diff_mode = False
        else:
            args.diff_mode = True
            self._handle_diff_arguments(args)
        
        return args
    
    
    def _handle_diff_arguments(self, args):
        import difflib, StringIO
        
        labels = args.label if args.label is not None else \
            [self._resolve_path(input) for input in args.input, args.input2]
        
        diff = ''.join(difflib.unified_diff(
            [self._to_unicode(line) for line in args.input.readlines()],
            [self._to_unicode(line) for line in args.input2.readlines()],
            *labels))
        
        args.input = StringIO.StringIO(
            'diff -u %s %s\n' % tuple(labels) + diff)
    
    
    def _handle_git_diff_arguments(self, args):
        path = self._resolve_path(args.input)
        args.label = [path, path]
        (args.input, args.input2) = (args.input2, args.new_file)
    
    
    def _resolve_path(self, stream):
        if isinstance(stream, basestring):
            return os.path.realpath(stream)
        elif stream is sys.stdin:
            return stream.name
        else:
            path = os.path.realpath(stream.name)
            return path if os.path.exists(path) else stream.name
    
    
    def _to_unicode(self, string):
        if isinstance(string, unicode):
            return string
        
        try:
            return unicode(string, locale.getpreferredencoding())
        except UnicodeDecodeError:
            encoding = chardet.detect(string)['encoding']
            return unicode(string, encoding, 'replace')


class Reader (object):
    __metaclass__ = abc.ABCMeta
    ansi_color_escape = re.compile(r'\x1B\[(\d+(;\d+)*)?m')
    
    
    @property
    def accepts_color(self):
        return True
    
    
    @abc.abstractmethod
    def close(self):
        pass
    
    
    @abc.abstractmethod
    def write(self, text):
        pass


class StreamReader (Reader):
    def __init__(self, stream):
        self._stream = codecs.getwriter(locale.getpreferredencoding())(stream)
    
    
    def close(self):
        if self._stream.stream is not sys.stdout:
            self._stream.close()
    
    
    def write(self, text):
        if not self.accepts_color:
            text = self.ansi_color_escape.sub('', text)
        
        try:
            self._stream.write(text)
        except IOError as error:
            if error.errno == errno.EPIPE:
                raise EOFError()
            else:
                raise


class ProgramReader (StreamReader):
    def __init__(self, command, stderr = None):
        try:
            self._process = subprocess.Popen(command,
                stderr = stderr,
                stdin = subprocess.PIPE)
        except OSError as error:
            if error.errno == errno.ENOENT:
                raise NotImplementedError
            else:
                raise
        
        super(ProgramReader, self).__init__(self._process.stdin)
    
    
    def close(self):
        super(ProgramReader, self).close()
        
        if not self.detached:
            self._process.communicate()
    
    
    @property
    def detached(self):
        return False


class TextReader (ProgramReader):
    def __init__(self, line = 1, **kargs):
        if 'command' in kargs:
            super(TextReader, self).__init__(**kargs)
            self._accepts_color = None
        else:
            try:
                super(TextReader, self).__init__(['less', '+%dg' % line])
                self._accepts_color = True
            except NotImplementedError:
                super(TextReader, self).__init__(['cmd', '/C', 'more'])
                self._accepts_color = False
    
    
    @property
    def accepts_color(self):
        if self._accepts_color is None:
            return super(TextReader, self).accepts_color
        else:
            return self._accepts_color


class DiffReader (TextReader):
    def __init__(self, terminal_only = False, **kargs):
        self._terminal_only = terminal_only
        
        if self._terminal_only:
            super(DiffReader, self).__init__(**kargs)
        else:
            super(DiffReader, self).__init__(
                command = ['kompare', '-o', '-'],
                stderr = file(os.path.devnull))
    
    
    @property
    def accepts_color(self):
        if self._terminal_only:
            return super(DiffReader, self).accepts_color
        else:
            return False
    
    
    @property
    def detached(self):
        if self._terminal_only:
            return super(DiffReader, self).detached
        else:
            return True


class Pager (Reader):
    backspace_control = re.compile(r'.\x08')
    
    
    def __init__(self, input,
            diff_mode = False,
            follow = False,
            inline_lines_threshold = 0.4,
            passthrough = False,
            terminal_only = False):
        
        self._input = input
        self._diff_mode = diff_mode
        self._follow = follow
        self._passthrough = passthrough
        self._terminal_only = terminal_only
        
        self._buffer = ''
        self._buffered_lines = 0
        self._line_separator = '\n'
        self._output = None
        
        if not sys.stdout.isatty() or self._follow:
            self._max_inline_lines = float('Infinity')
        else:
            (rows, columns) = self._guess_terminal_size()
            self._max_inline_lines = int(round(rows * inline_lines_threshold))
    
    
    def __iter__(self):
        (detected, encoding) = (False, locale.getpreferredencoding())
        
        for line in self._input:
            try:
                if not isinstance(line, unicode):
                    line = line.decode(encoding)
            except UnicodeDecodeError:
                if detected:
                    raise
                
                text = self._buffer.encode() + line
                (detected, encoding) = (True, chardet.detect(text)['encoding'])
                yield self.backspace_control.sub('', line.decode(encoding))
            else:
                yield self.backspace_control.sub('', line)
        
        if self._follow:
            import time
            
            (text, self._buffer) = (self._buffer, '')
            self._setup_output(text)
            self._display(text)
            
            while True:
                line = self._input.readline()
                
                if len(line) == 0:
                    previous_size = os.path.getsize(self._input.name)
                    time.sleep(1)
                    
                    if os.path.getsize(self._input.name) < previous_size:
                        self._input.seek(0)
                else:
                    yield self.backspace_control.sub('', line.decode(encoding))
        
        raise StopIteration
    
    
    def close(self):
        self._input.close()
        
        if self._buffer != '':
            self._setup_output(self._buffer)
            self._display(self._buffer)
        
        if self._output is not None:
            self._output.close()
    
    
    def write(self, text):
        if self._output is None:
            self._buffer += text
            self._buffered_lines += text.count(self._line_separator)
            
            if self._buffered_lines <= self._max_inline_lines:
                return
            
            (text, self._buffer) = (self._buffer, '')
            self._setup_output(text)
        
        self._display(text)
    
    
    def _display(self, text):
        if self._passthrough or (self._lexer is None):
            self._output.write(text)
        else:
            self._output.write(pygments.highlight(
                self.ansi_color_escape.sub('', text),
                self._lexer,
                self._formatter))
    
    
    def _guess_lexer(self, text):
        if self._passthrough:
            return None
        elif self._diff_mode:
            return pygments.lexers.DiffLexer(stripnl = False)
        else:
            clean_text = self.ansi_color_escape.sub('', text)
            
            try:
                return pygments.lexers.guess_lexer_for_filename(
                    self._input.name, clean_text, stripnl = False)
            except pygments.util.ClassNotFound:
                pass
            
            try:
                return pygments.lexers.guess_lexer(clean_text,
                    stripnl = False)
            except TypeError:
                # See <http://bitbucket.org/birkenfeld/pygments-main/issue/618/>
                # $ echo .text | pygmentize -g
                pass
            
            return None
    
    
    def _guess_terminal_size(self):
        def ioctl_GWINSZ(fd):
            import fcntl, termios
            size_data = fcntl.ioctl(fd, termios.TIOCGWINSZ, b'1234')
            (rows, columns) = struct.unpack(b'hh', size_data)
            return (rows, columns)
        
        for stream in sys.stdin, sys.stdout, sys.stderr:
            try:
                return ioctl_GWINSZ(stream.fileno())
            except:
                continue
        
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            try:
                return ioctl_GWINSZ(fd)
            finally:
                os.close(fd)
        except:
            pass
        
        try:
            stty = subprocess.Popen(['stty', 'size'],
                stdout = subprocess.PIPE)
            
            (rows, columns) = stty.stdout.read().split()
            return (rows, columns)
        except:
            pass
        
        return (0, 0)
    
    
    def _setup_output(self, text):
        self._lexer = self._guess_lexer(text)
        go_to_line = getattr(self._input, 'line', 1)
        
        if self._buffered_lines <= self._max_inline_lines:
            self._output = StreamReader(sys.stdout)
        elif self._diff_mode or \
                isinstance(self._lexer, pygments.lexers.DiffLexer):
            try:
                self._output = DiffReader(
                    line = go_to_line,
                    terminal_only = self._terminal_only)
            except NotImplementedError:
                self._output = TextReader(line = go_to_line)
        else:
            self._output = TextReader(line = go_to_line)
        
        if self._lexer is not None:
            self._formatter = pygments.formatters.Terminal256Formatter()


try:
    (args, unknown_args) = ArgumentsParser().parse_known_args()
except KeyboardInterrupt:
    print
    sys.exit()
except argparse.ArgumentTypeError as error:
    sys.exit(str(error))
except IOError as error:
    if error.errno == errno.ENOENT:
        sys.exit(str(error))
    else:
        raise

pager = Pager(args.input,
    diff_mode = args.diff_mode,
    follow = args.follow,
    passthrough = args.passthrough,
    terminal_only = args.terminal_only)

try:
    for line in pager:
        pager.write(line)
except KeyboardInterrupt:
    print
except EOFError:
    pass

pager.close()
