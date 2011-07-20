#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard library:
from __future__ import unicode_literals
import errno, os, sys


# Not an abstract base class for performance.
class StreamInput:
    def __init__(self, stream, name,
            encoding = 'UTF-8',
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


class FileInput (StreamInput):
    def __init__(self, path):
        StreamInput.__init__(self, open(path), name = os.path.abspath(path))


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
    def __init__(self, path, ls_args):
        SubProcessInput.__init__(self, ['ls', path] + ls_args,
            name = os.path.abspath(path),
            passthrough_mode = True)


class PerlDocInput (SubProcessInput):
    def __init__(self, module):
        SubProcessInput.__init__(self, ['perldoc', '-t', module],
            name = module)


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
        
        StreamInput.__init__(self, urllib.urlopen(uri), name = uri)


class Options:
    # TODO: Too long, refactor.
    def __init__(self,
            diff_mode = False,
            default_protocol = 'http://',
            inline_lines_threshold = 0.4,
            passthrough_mode = False,
            self_path = sys.argv[0],
            self_repr = 'self',
            stdin_stream = sys.stdin,
            stdin_repr = '-',
            stdout_stream = sys.stdout,
            terminal_only = False,
            visible_white_space = False):
        
        # argparse isn't used for performance.
        import getopt
        
        try:
            # No long options available for performance.
            (options, arguments) = getopt.getopt(sys.argv[1:],
                'df:hi:l:m:p:s:tw')
        except getopt.GetoptError as error:
            sys.exit(str(error))
        
        self.default_protocol = default_protocol
        self.diff_mode = diff_mode
        self.inline_lines_threshold = inline_lines_threshold
        self.ls_arguments = []
        self.passthrough_mode = passthrough_mode
        self.self_path = self_path
        self.self_repr = self_repr
        self.stdin_stream = stdin_stream
        self.stdin_repr = stdin_repr
        self.stdout_stream = stdout_stream
        self.terminal_only = terminal_only
        self.visible_white_space = visible_white_space
        
        if len(arguments) > 2:
            options.insert(0, ('-h', ''))
        
        for option, value in options:
            if option == '-d':
                self.passthrough_mode = True
            elif option == '-h':
                print '''
Automatic pager with syntax highlighting, diff support and file/text search.

Usage:
  pager     [options] [input-1 [input-2]]
  search    [options] [input]*

Options:
  -d        passthrough mode, don't attempt to syntax highlight input (faster)
  -f        list files with names matching the given pattern
  -h        show usage help
  -i        standard input string representation, defaults to "%s"
  -l        option for "ls", when listing directories
  -m        list file matches for the given pattern
  -p        protocol for URI's with missing scheme, defaults to "%s"
  -s        this script's path string representation, defaults to "%s"
  -t        use terminal only, no graphical interfaces
  -w        convert blank spaces to visible characters (slower)

An input can be a path, an URI, a Perl module name, standard input or this script's (given their string representation). If given a directory, its' contents are listed via "ls".

The input's name can also be suffixed with a colon followed by a line number to scroll to, if possible.
'''.strip() % (stdin_repr, default_protocol, self_repr)
                sys.exit()
            elif option == '-i':
                self.stdin_repr = value
            if option == '-l':
                self.ls_arguments.append(value)
            elif option == '-p':
                self.default_protocol = value
            elif option == '-s':
                self.self_repr = value
            elif option == '-t':
                self.terminal_only = True
            elif option == '-w':
                self.visible_white_space = True
        
        if len(arguments) == 2:
            self.input = self._open_diff_input(map(self._open_input, arguments))
        else:
            if len(arguments) == 0:
                if self.stdin_stream.isatty():
                    self.input = self._open_input(os.curdir)
                else:
                    self.input = StreamInput(self.stdin_stream,
                        name = self.stdin_repr)
            elif len(arguments) == 1:
                inputs = []
                
                if not self.stdin_stream.isatty():
                    inputs.append(StreamInput(self.stdin_stream,
                        name = self.stdin_repr))
                
                inputs.append(self._open_input(arguments[0]))
                
                if len(inputs) > 1:
                    self.input = self._open_diff_input(inputs)
                else:
                    self.input = inputs[0]
        
        if self.input.passthrough_mode:
            self.passthrough_mode = True
    
    
    def _open_diff_input(self, inputs):
        import difflib, cStringIO
        
        labels = [input.name.encode('UTF-8') for input in inputs]
        header = b'diff -u %s %s' % tuple(labels)
        
        # TODO: Use the generator directly to stream by line instead of
        # concatenating into a StringIO object, to improve performance.
        diff = cStringIO.StringIO(
            header + b'\n' + b''.join(difflib.unified_diff(
                inputs[0].stream.readlines(),
                inputs[1].stream.readlines(),
                *labels)))
        
        for input in inputs:
            input.close()
        
        self.diff_mode = True
        return StreamInput(diff, name = header)
    
    
    # TODO: Too long, refactor.
    def _open_input(self, path):
        # Check common and fail-fast cases first for performance.
        
        try:
            return FileInput(path)
        except IOError as error:
            if error.errno == errno.EISDIR:
                return DirectoryInput(path, self.ls_arguments)
            
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
                
                import re
                
                go_to_line = re.search(
                    r'^ (.+?) : ([+-]? (?: [1-9] | \d{2,})) $', path,
                    re.VERBOSE)
                
                if go_to_line is not None:
                    (path, line) = go_to_line.groups()
                    
                    try:
                        stream = self._open_input(path)
                        stream.line = int(line)
                        return stream
                    except IOError:
                        pass
            
            raise error


# Not an abstract base class for performance.
class Output:
    def close(self):
        raise NotImplementedError()


class StreamOutput (Output):
    def __init__(self, stream, formatter = None, passthrough_mode = False):
        self.formatter = formatter
        self.passthrough_mode = passthrough_mode
        self.stream = stream
    
    
    def close(self):
        if self.stream is not sys.stdout:
            self.stream.close()


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

class Pager (Output):
    def __init__(self, options):
        self._ansi_color_re = None
        self._lexer = None
        self._options = options
        self._output = None
        
        # TODO: Use None when unavailable for performance?
        if options.stdout_stream.isatty():
            (rows, self._terminal_width) = self._guess_terminal_size()
            self._max_inline_lines = int(round(
                rows * options.inline_lines_threshold))
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
        
        for line in self._options.input.stream:
            buffered_lines.append(line)
            wrapped_lines += int(round(
                (len(line) - 1.0) / self._terminal_width))
            
            if (len(buffered_lines) + wrapped_lines) > self._max_inline_lines:
                self._flush_buffer(buffered_lines, TextOutput, DiffOutput)
                break
        else:
            self._flush_buffer(buffered_lines,
                lambda options: StreamOutput(self._options.stdout_stream),
                lambda options: StreamOutput(self._options.stdout_stream))
            return
        
        if self._options.passthrough_mode:
            for line in self._options.input.stream:
                try:
                    self._output.stream.write(line)
                except IOError as error:
                    if error.errno == errno.EPIPE:
                        break
                    else:
                        raise
        elif self._output.passthrough_mode:
            for line in self._options.input.stream:
                try:
                    self._output.stream.write(self._ansi_color_re.sub(b'', line))
                except IOError as error:
                    if error.errno == errno.EPIPE:
                        break
                    else:
                        raise
        else:
            from pygments import highlight as pygments_highlight
            encoding = self._options.input.encoding
            
            # TODO: Highlight in batches to amortize the performance penalty?
            # E.g. read stream in chunked bytes.
            for line in self._options.input.stream:
                try:
                    self._output.stream.write(
                        pygments_highlight(
                            self._ansi_color_re.sub(b'', line).decode(encoding),
                            self._lexer,
                            self._output.formatter).encode(encoding))
                except IOError as error:
                    if error.errno == errno.EPIPE:
                        break
                    else:
                        raise
    
    
    # TODO: Too long, refactor.
    def _flush_buffer(self, buffered_lines, text_output, diff_output):
        text = b''.join(buffered_lines)
        
        if self._options.passthrough_mode:
            self._output = text_output(self._options)
            self._output.stream.write(text)
            return
        
        import re
        self._ansi_color_re = re.compile(br'\x1B\[(?:\d+(?:;\d+)*)?m')
        
        if self._options.diff_mode:
            from pygments.lexers.text import DiffLexer
            self._lexer = DiffLexer(stripnl = False)
            clean_text = text
            
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
                    self._output.stream.write(text)
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
        
        if self._output.formatter is None:
            from pygments.formatters.terminal256 import Terminal256Formatter
            self._output.formatter = Terminal256Formatter()
        
        from pygments import highlight as pygments_highlight
        encoding = self._options.input.encoding
        
        if self._output.passthrough_mode:
            self._output.stream.write(clean_text)
        else:
            if self._options.visible_white_space:
                self._lexer.add_filter('whitespace', spaces = True)
            
            self._output.stream.write(
                pygments_highlight(clean_text.decode(encoding), self._lexer,
                    self._output.formatter).encode(encoding))
    
    
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
    pager = Pager(Options())
    
    try:
        pager.display()
    finally:
        pager.close()
