#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# TODO: Implement file/text search.
# TODO: Fix line length counting when the input contains ANSI color codes?
# TODO: Allow special glob input?
#       ./show.py .py # '*.py'
# TODO: Add filter to highlight trailing white-space?
# TODO: Add option to follow file? (Automatically if it changes size?)
# TODO: Print header for "less" to show the input's path?
#       perl -MTerm::ANSIColor -we "print colored(sprintf('%-80s', 'test'), 'bright_white on_black')"
# TODO: Convert to C++ for speed? http://www.cython.org/
#       Or re-use existing programs?
#       highlight -A source.c
#           http://www.andre-simon.de/doku/highlight/en/highlight.html
#       source-highlight -f esc -i source.c
#           http://www.gnu.org/software/src-highlite/
# TODO: Add documentation and tests.


# Standard library:
from __future__ import unicode_literals
import errno, os, sys


# Not an abstract base class for performance.
class StreamInput:
    DEFAULT_ENCODING = 'UTF-8'
    
    
    def __init__(self, stream, name,
            encoding = DEFAULT_ENCODING,
            line = 1,
            passthrough_mode = False):
        
        self.encoding = encoding
        self.line = line
        self.name = name
        self.stream = stream
        
        # This option exists mainly for performance, e.g. when listing
        # directories using "ls" don't bother syntax highlighting its output.
        self.passthrough_mode = passthrough_mode
    
    
    def close(self):
        self.stream.close()


class DiffInput (StreamInput):
    def __init__(self, input_left, input_right):
        import difflib, cStringIO
        
        labels = [input.name.encode(StreamInput.DEFAULT_ENCODING)
            for input in (input_left, input_right)]
        header = b'diff -u %s %s' % tuple(labels)
        
        # TODO: Use the generator directly to stream by line instead of
        # concatenating into a StringIO object, to improve performance?
        diff = cStringIO.StringIO(
            header + b'\n' + b''.join(difflib.unified_diff(
                self._read_lines(input_left),
                self._read_lines(input_right),
                *labels)))
        
        StreamInput.__init__(self, diff, name = header)
    
    
    def _read_lines(self, input):
        lines = input.stream.readlines()
        encoding = input.encoding
        
        from codecs import lookup as codecs_lookup
        input.close()
        
        if codecs_lookup(encoding).name == 'utf-8':
            return lines
        else:
            input.encoding = StreamInput.DEFAULT_ENCODING
            return [l.decode(encoding).encode(input.encoding) for l in lines]


class FileInput (StreamInput):
    def __init__(self, path):
        StreamInput.__init__(self, open(path), name = os.path.abspath(path))


class SconsDbInput (StreamInput):
    @staticmethod
    def handles(path):
        return path.endswith('.sconsign.dblite')
    
    
    def __init__(self, path, options):
        import pkg_resources
        
        [scons_package] = pkg_resources.require('SCons')
        sys.path.append(os.path.join(
            scons_package.location, 'scons-' + scons_package.version))
        
        import SCons.dblite, pickle, pprint, cStringIO
        
        scons_db = SCons.dblite.open(path)
        scons_db_dict = {}
        
        for key in scons_db:
            scons_db_dict[key] = pickle.loads(scons_db[key])
        
        StreamInput.__init__(self,
            stream = cStringIO.StringIO(pprint.pformat(scons_db_dict)),
            name = path)


class SubProcessInput (StreamInput):
    def __init__(self, args, **kargs):
        import subprocess
        
        process = subprocess.Popen(args,
            stderr = open(os.devnull),
            stdout = subprocess.PIPE)
        
        if process.wait() != 0:
            # No error message for performance, since it isn't shown anyway.
            raise IOError()
        
        StreamInput.__init__(self, stream = process.stdout, **kargs)
        self._process = process
    
    
    def close(self):
        self._process.communicate()
        StreamInput.close(self)


class DirectoryInput (SubProcessInput):
    def __init__(self, ls_args, *paths):
        SubProcessInput.__init__(self, ['ls'] + ls_args + list(paths),
            name = os.path.abspath(paths[0]) if len(paths) == 1 else os.getcwd(),
            passthrough_mode = True)


class ObjectFileInput (SubProcessInput):
    @staticmethod
    def handles(path):
        path = path.lower()
        
        # No regular expression used for performance.
        return path.endswith('.o') \
            or path.endswith('.os') \
            or path.endswith('.so')
    
    
    def __init__(self, path, options):
        SubProcessInput.__init__(self,
            args = ['nm', '-C'] + options.nm_arguments + [path],
            name = path,
            passthrough_mode = True)


class PerlDocInput (SubProcessInput):
    def __init__(self, module):
        SubProcessInput.__init__(self, ['perldoc', '-t', module], name = module)


class TarFileInput (SubProcessInput):
    @staticmethod
    def handles(path):
        path = path.lower()
        
        # No regular expression used for performance. List of extensions taken
        # from "lesspipe".
        return path.endswith('.tar.gz') \
            or path.endswith('.tgz') \
            or path.endswith('.tar.z') \
            or path.endswith('.tar.dz') \
            or path.endswith('.tar')
    
    
    def __init__(self, path, options):
        SubProcessInput.__init__(self,
            args = ['tar', '-t'] + options.tar_arguments + ['-f', path],
            name = path,
            passthrough_mode = True)


class UriInput (StreamInput):
    def __init__(self, uri, default_protocol):
        import urllib, urlparse
        parts = urlparse.urlparse(uri)
        
        if parts.scheme == '':
            clean_uri = urllib.unquote(parts.path)
            clean_parts = urlparse.urlparse(clean_uri)
            
            if clean_parts.path == parts.path:
                uri = default_protocol + uri
            elif clean_parts.scheme == '':
                uri = default_protocol + clean_uri
            else:
                uri = clean_uri
        
        from email import message_from_string as email_from_string
        
        stream = urllib.urlopen(uri)
        charset = email_from_string(str(stream.headers)).get_content_charset()
        
        if charset is None:
            StreamInput.__init__(self, stream, name = uri)
        else:
            StreamInput.__init__(self, stream, name = uri, encoding = charset)


class ZipFileInput (SubProcessInput):
    @staticmethod
    def handles(path):
        # No regular expression used for performance.
        return path.lower().endswith('.zip')
    
    
    def __init__(self, path, options):
        SubProcessInput.__init__(self,
            args = ['unzip', '-l'] + options.unzip_arguments + [path],
            name = path,
            passthrough_mode = True)


class Options:
    # Check common cases first for performance.
    INPUT_HANDLERS = [
        TarFileInput,
        ZipFileInput,
        ObjectFileInput,
        SconsDbInput,
    ]
    
    
    # TODO: Too long, refactor.
    def __init__(self):
        # argparse isn't used for performance.
        import getopt
        
        try:
            # No long options available for performance.
            (options, arguments) = getopt.getopt(sys.argv[1:],
                'a:df:hi:j:l:L:m:no:p:r:s:tuwz:')
        except getopt.GetoptError as error:
            sys.exit(str(error))
        
        self.default_protocol = 'http://'
        self.diff_mode = False
        self.line_nr_field_width = 4
        self.ls_arguments = []
        self.nm_arguments = []
        self.paging_threshold_ratio = 0.4
        self.passthrough_mode = False
        self.self_path = sys.argv[0]
        self.self_repr = 'self'
        self.show_line_nrs = False
        self.stdin_stream = sys.stdin
        self.stdin_repr = '-'
        self.stdout_stream = sys.stdout
        self.tar_arguments = []
        self.terminal_only = False
        self.unzip_arguments = []
        self.visible_white_space = False
        
        for option, value in options:
            if option == '-a':
                self.tar_arguments.append(value)
            elif option == '-d':
                self.passthrough_mode = True
            elif option == '-h':
                print '''
Automatic pager with syntax highlighting and diff support.

An input can be a path, an URI, a Perl module name, a tar archive, an object
file, standard input or this script's (by their string representation).

The input's name can also be suffixed with a colon followed by a line number to
scroll to, if possible.

Usage:
  pager     [options] [input [input]]
  ls        [options] input{3,}

Options:
  -a        option for "tar", when viewing tar files
  -d        passthrough mode, don't attempt to syntax highlight input (faster)
  -h        show usage help
  -i        standard input string representation, defaults to "%s"
  -j        line number right-justified field width, defaults to %s
  -l        option for "ls", when listing directories
  -L        ignored for Subversion compatibility
  -n        show line numbers (slower)
  -o        option for "nm", when viewing object files
  -p        protocol for URI's with missing scheme, defaults to "%s"
  -r        paging ratio of input lines / terminal height, defaults to %s (%%)
  -s        this script's path string representation, defaults to "%s"
  -t        use terminal only, no graphical interfaces
  -u        ignored for diff compatibility
  -w        convert blank spaces to visible characters (slower)
  -z        option for "unzip", when viewing ZIP files
'''.strip() % (
    self.stdin_repr, self.line_nr_field_width, self.default_protocol,
    self.paging_threshold_ratio, self.self_repr)
                sys.exit()
            elif option == '-i':
                self.stdin_repr = value
            elif option == '-j':
                try:
                    self.line_nr_field_width = int(value)
                    if self.line_nr_field_width < 2:
                        raise ValueError()
                except ValueError:
                    sys.exit('invalid line number field width: ' + value)
            elif option == '-l':
                self.ls_arguments.append(value)
            elif option == '-n':
                self.show_line_nrs = True
            elif option == '-o':
                self.nm_arguments.append(value)
            elif option == '-p':
                self.default_protocol = value
            elif option == '-r':
                try:
                    r = float(value)
                    self.paging_threshold_ratio = r
                    import math
                    
                    if math.isinf(r) or math.isnan(r) or (r < 0) or (r > 1):
                        raise ValueError()
                except ValueError:
                    sys.exit('invalid paging ratio value: ' + value)
            elif option == '-s':
                self.self_repr = value
            elif option == '-t':
                self.terminal_only = True
            elif option == '-w':
                self.visible_white_space = True
            elif option == '-z':
                self.unzip_arguments.append(value)
        
        if len(arguments) > 2:
            self.input = DirectoryInput(self.ls_arguments, *arguments)
        elif len(arguments) == 2:
            self.ls_arguments.append('--color=never')
            self.input = DiffInput(*map(self._open_input, arguments))
            self.diff_mode = True
        elif len(arguments) == 1:
                self.input = self._open_input(arguments[0])
        elif len(arguments) == 0:
            if self.stdin_stream.isatty():
                self.input = self._open_input(os.curdir)
            else:
                self.input = StreamInput(self.stdin_stream,
                    name = self.stdin_repr)
        
        if self.input.passthrough_mode:
            self.passthrough_mode = True
    
    
    # TODO: Too long, refactor.
    def _open_input(self, path):
        for input_handler in self.INPUT_HANDLERS:
            if input_handler.handles(path):
                try:
                    return input_handler(path, self)
                except IOError:
                    pass
        
        # Check common and fail-fast cases first for performance.
        try:
            return FileInput(path)
        except IOError as error:
            if error.errno == errno.EISDIR:
                return DirectoryInput(self.ls_arguments, path)
            
            if error.errno == errno.ENOENT:
                if path == self.stdin_repr:
                    return StreamInput(self.stdin_stream,
                        name = self.stdin_repr)
                
                try:
                    return PerlDocInput(path)
                except IOError:
                    pass
                
                if path == self.self_repr:
                    return FileInput(self.self_path)
                
                # No re.VERBOSE option for performance.
                import re
                go_to_line = re.search(r'^(.+?):([+-]?(?:[1-9]|\d{2,}))$', path)
                
                if go_to_line is not None:
                    (path, line) = go_to_line.groups()
                    
                    try:
                        stream = self._open_input(path)
                        stream.line = int(line)
                        return stream
                    except IOError:
                        pass
                
                import httplib
                
                try:
                    return UriInput(path, self.default_protocol)
                except httplib.InvalidURL:
                    pass
                except IOError as uri_error:
                    if uri_error.filename is not None:
                        import urlparse
                        parts = urlparse.urlparse(path)
                        
                        try:
                            return self._open_input(parts.path)
                        except IOError:
                            pass
            
            sys.exit(str(error))


# Not an abstract base class for performance.
class Output:
    def close(self):
        raise NotImplementedError()


class StreamOutput (Output):
    def __init__(self, stream, formatter = None, passthrough_mode = False):
        self.formatter = formatter
        self.passthrough_mode = passthrough_mode
        self._stream = stream
    
    
    def close(self):
        if self._stream is not sys.stdout:
            self._stream.close()
    
    
    def write(self, *data):
        for string in data:
            self._stream.write(string)


class SubProcessOutput (StreamOutput):
    def __init__(self, args, detached = False, stderr = None, **kargs):
        import subprocess
        
        try:
            self._process = subprocess.Popen(args,
                stderr = stderr,
                stdin = subprocess.PIPE)
        except OSError as error:
            if error.errno == errno.ENOENT:
                raise NotImplementedError
            else:
                raise
        
        import signal
        
        # TODO: Possible race condition between starting the process and
        # registering the signal handler?
        signal.signal(signal.SIGINT,
            lambda sig_int, frame: self._process.send_signal(sig_int))
        
        StreamOutput.__init__(self, self._process.stdin, **kargs)
        self._detached = detached
    
    
    def close(self):
        if not self._detached:
            self._process.communicate()
        
        StreamOutput.close(self)


class TextOutput (SubProcessOutput):
    def __init__(self, options, **kargs):
        if 'args' in kargs:
            SubProcessOutput.__init__(self, **kargs)
        else:
            from pygments.formatters.terminal256 import Terminal256Formatter
            
            SubProcessOutput.__init__(self,
                args = ['less', '+%dg' % options.input.line],
                formatter = Terminal256Formatter())


class DiffOutput (TextOutput):
    def __init__(self, options):
        if options.terminal_only:
            TextOutput.__init__(self, options)
        else:
            TextOutput.__init__(self, options,
                args = ['kompare', '-o', '-'],
                detached = True,
                passthrough_mode = True,
                stderr = open(os.devnull))
            
            self.write = self._kompare_write
            self._last_string = b''
    
    
    # Fix parse error when the diff header has a trailing tab character after
    # file names (e.g. Git built-in diff output).
    def _kompare_write(self, *data):
        for string in data:
            strings = string.split(b'\n')
            
            for string in strings:
                if string == b'':
                    continue
                
                is_header = \
                    (self._last_string.startswith(b'index ') \
                        and string.startswith(b'--- a/')) \
                    or (self._last_string.startswith(b'--- a/') \
                        and string.startswith(b'+++ b/'))
                
                if is_header:
                    TextOutput.write(self, string.rstrip(b'\t') + b'\n')
                else:
                    TextOutput.write(self, string + b'\n')
                
                self._last_string = string


class Pager (Output):
    @staticmethod
    def start():
        pager = Pager(Options())
        
        try:
            pager.display()
        except UnicodeDecodeError as error:
            pager.close()
            sys.exit('Invalid %s data, binary file? (%s)' \
                % (StreamInput.DEFAULT_ENCODING, error))
        finally:
            pager.close()
    
    
    def __init__(self, options):
        self._ansi_color_re = None
        self._lexer = None
        self._options = options
        self._output = None
        self._output_encoding = None
        
        # TODO: Use None when unavailable for performance?
        if options.stdout_stream.isatty():
            (rows, self._terminal_width) = self._guess_terminal_size()
            self._max_inline_lines = int(round(
                rows * options.paging_threshold_ratio))
        else:
            self._max_inline_lines = float('Infinity')
            self._terminal_width = float('Infinity')
    
    
    def close(self):
        try:
            self._options.input.close()
        finally:
            if self._output is not None:
                self._output.close()
    
    
    # TODO: Too long, refactor.
    def display(self):
        buffered_lines = []
        wrapped_lines = 0
        
        try:
            for line in self._options.input.stream:
                buffered_lines.append(line)
                wrapped_lines += int(round(
                    (len(line) - 1.0) / self._terminal_width))
                
                if (len(buffered_lines) + wrapped_lines) > self._max_inline_lines:
                    self._flush_buffer(buffered_lines, TextOutput, DiffOutput)
                    break
            else:
                if len(buffered_lines) > 0:
                    self._flush_buffer(buffered_lines,
                        lambda options: StreamOutput(options.stdout_stream),
                        lambda options: StreamOutput(options.stdout_stream))
                
                return
            
            if self._options.show_line_nrs:
                line_nr = len(buffered_lines)
                width = self._options.line_nr_field_width - 1
            
            if self._options.passthrough_mode:
                if self._options.show_line_nrs:
                    for line in self._options.input.stream:
                        line_nr += 1
                        self._output.write(str(line_nr).rjust(width) + b' ', line)
                else:
                    for line in self._options.input.stream:
                        self._output.write(line)
            elif self._output.passthrough_mode:
                if self._options.show_line_nrs:
                    for line in self._options.input.stream:
                        line_nr += 1
                        self._output.write(
                            str(line_nr).rjust(width) + b' ',
                            self._ansi_color_re.sub(b'', line))
                else:
                    for line in self._options.input.stream:
                        self._output.write(self._ansi_color_re.sub(b'', line))
            else:
                from pygments import highlight as pygments_highlight
                encoding = self._options.input.encoding
                
                # TODO: Highlight in batches to amortize the performance penalty?
                # E.g. read stream in chunked bytes.
                
                if self._options.show_line_nrs:
                    for line in self._options.input.stream:
                        line_nr += 1
                        self._output.write(str(line_nr).rjust(width) + b' ')
                        
                        self._output.write(pygments_highlight(
                            self._ansi_color_re.sub(b'', line).decode(encoding),
                            self._lexer,
                            self._output.formatter).encode(self._output_encoding))
                else:
                    for line in self._options.input.stream:
                        self._output.write(pygments_highlight(
                            self._ansi_color_re.sub(b'', line).decode(encoding),
                            self._lexer,
                            self._output.formatter).encode(self._output_encoding))
        except IOError as error:
            if error.errno != errno.EPIPE:
                raise
        except KeyboardInterrupt:
            self._options.stdout_stream.write('\n')
    
    
    # TODO: Too long, refactor.
    def _flush_buffer(self, buffered_lines, text_output, diff_output):
        if self._options.passthrough_mode:
            self._output = text_output(self._options)
            
            if self._options.show_line_nrs:
                self._flush_buffer_line_nrs(buffered_lines)
            else:
                self._output.write(*buffered_lines)
            return
        
        text = b''.join(buffered_lines)
        
        # No re.VERBOSE option for performance.
        import re
        self._ansi_color_re = re.compile(br'\x1B\[(?:\d+(?:;\d+)*)?m')
        
        if self._options.diff_mode:
            from pygments.lexers.text import DiffLexer
            self._lexer = DiffLexer(stripnl = False)
            
            try:
                self._output = diff_output(self._options)
            except NotImplementedError:
                self._output = text_output(self._options)
        else:
            from pygments.util import ClassNotFound as LexerClassNotFound
            clean_text = self._ansi_color_re.sub(b'', text)
            
            try:
                from pygments.lexers import guess_lexer_for_filename
                self._lexer = guess_lexer_for_filename(self._options.input.name,
                    clean_text, stripnl = False)
            except LexerClassNotFound:
                try:
                    (self._lexer, matches) = self._guess_lexer(clean_text,
                        stripnl = False)
                    
                    if (matches > 0) and (len(clean_text) != len(text)):
                        # More than one lexer was found with the same weight
                        # and the input was already colored, so preserve it.
                        # No error message for performance, since it isn't shown
                        # anyway.
                        raise LexerClassNotFound()
                except (TypeError, LexerClassNotFound):
                    # TypeError might unexpectedly be raised:
                    # http://bitbucket.org/birkenfeld/pygments-main/issue/618/
                    self._options.passthrough_mode = True
                    self._output = text_output(self._options)
                    
                    if self._options.show_line_nrs:
                        self._flush_buffer_line_nrs(buffered_lines)
                    else:
                        self._output.write(text)
                    return
            
            # isinstance() isn't used for performance.
            if self._lexer.name == 'Diff':
                self._options.diff_mode = True
                
                try:
                    self._output = diff_output(self._options)
                except NotImplementedError:
                    self._output = text_output(self._options)
            else:
                self._output = text_output(self._options)
            
            if not self._options.show_line_nrs:
                text = clean_text
        
        if self._output.passthrough_mode:
            if self._options.show_line_nrs:
                self._flush_buffer_line_nrs(
                    [self._ansi_color_re.sub(b'', l) for l in buffered_lines])
            else:
                self._output.write(text)
            return
        
        import locale
        from pygments import highlight as pygments_highlight
        
        self._output_encoding = locale.getpreferredencoding()
        
        if self._output.formatter is None:
            from pygments.formatters.terminal256 import Terminal256Formatter
            self._output.formatter = Terminal256Formatter()
        
        if self._options.visible_white_space:
            self._lexer.add_filter('whitespace', spaces = True, tabs = True)
        
        if self._options.show_line_nrs:
            lines = []
            
            for line in buffered_lines:
                line = self._ansi_color_re.sub(b'', line)
                
                lines.append(pygments_highlight(
                    line.decode(self._options.input.encoding),
                    self._lexer,
                    self._output.formatter).encode(self._output_encoding))
            
            self._flush_buffer_line_nrs(lines)
        else:
            self._output.write(pygments_highlight(
                text.decode(self._options.input.encoding),
                self._lexer,
                self._output.formatter).encode(self._output_encoding))
    
    
    def _flush_buffer_line_nrs(self, buffered_lines):
        width = self._options.line_nr_field_width - 1
        
        for line_nr, line in enumerate(buffered_lines, start = 1):
            self._output.write(str(line_nr).rjust(width) + b' ' + line)
    
    
    # Used instead of pygments.lexers.guess_lexer() to get a count of ambiguous
    # matches.
    def _guess_lexer(self, text, **options):
        from pygments.lexers import _iter_lexerclasses as lexer_classes
        
        (best_lexer, best_weight) = (None, 0.0)
        matches = 0
        
        for lexer in lexer_classes():
            weight = lexer.analyse_text(text)
            
            if weight == 1.0:
                return (lexer(**options), 0)
            elif weight > best_weight:
                (best_lexer, best_weight) = (lexer, weight)
                matches = 0
            elif weight == best_weight:
                matches += 1
        
        if best_lexer is None:
            # No error message for performance, since it isn't shown anyway.
            # Also, pygments.util.ClassNotFound() isn't used to avoid an import.
            raise TypeError()
        
        return (best_lexer(**options), matches)
    
    
    def _guess_terminal_size(self):
        def ioctl_GWINSZ(fd):
            import fcntl, struct, termios
            return struct.unpack(b'hh',
                fcntl.ioctl(fd, termios.TIOCGWINSZ, b'1234'))
        
        for stream in [
                self._options.stdin_stream,
                self._options.stdout_stream,
                sys.stderr]:
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
            import subprocess
            stty = subprocess.Popen(['stty', 'size'], stdout = subprocess.PIPE)
            return stty.stdout.read().split()
        except:
            pass
        
        return (float('Infinity'), float('Infinity'))


if __name__ == '__main__':
    Pager.start()
