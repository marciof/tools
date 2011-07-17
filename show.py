#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard library:
from __future__ import unicode_literals
import errno, os, sys


# NOTE: No abstract base class for performance.
class StreamInput:
    def __init__(self, stream, name, line = 1):
        self.line = line
        self.name = name
        self.stream = stream
    
    
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
            raise IOError()
        
        StreamInput.__init__(self, stream = process.stdout, **kargs)
        self._process = process
    
    
    def close(self):
        self._process.communicate()
        StreamInput.close(self)


class DirectoryInput (SubProcessInput):
    def __init__(self, path, ls_args):
        SubProcessInput.__init__(self, ['ls'] + ls_args,
            name = os.path.abspath(path))


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


class PerlDocInput (SubProcessInput):
    def __init__(self, module):
        SubProcessInput.__init__(self, ['perldoc', '-t', module],
            name = module)


def open_input(path,
        default_protocol = 'http://',
        ls_args = [],
        self_path = sys.argv[0],
        self_repr = 'self',
        stdin_repr = '-'):
    
    try:
        return FileInput(path)
    except IOError as error:
        exception = sys.exc_info()
    
    if error.errno == errno.EISDIR:
        return DirectoryInput(path, ls_args)
    
    if error.errno == errno.ENOENT:
        if path == stdin_repr:
            return StreamInput(sys.stdin, name = stdin_repr)
        
        try:
            return PerlDocInput(path)
        except IOError:
            pass
        
        if path == self_repr:
            return FileInput(self_path)
        
        import httplib
        
        try:
            return UriInput(path, default_protocol)
        except httplib.InvalidURL:
            pass
        except IOError as uri_error:
            if uri_error.filename is not None:
                import urlparse
                parts = urlparse.urlparse(path)
                
                try:
                    return open_input(parts.path,
                        default_protocol, ls_args,
                        self_path, self_repr, stdin_repr)
                except IOError:
                    pass
        
        import re
        go_to_line = re.search(r'^ (.+?) : ([+-]? (?: [1-9] | \d{2,})) $', path,
            re.VERBOSE)
        
        if go_to_line is not None:
            (path, line) = go_to_line.group(1, 2)
            
            try:
                stream = open_input(path,
                    default_protocol, ls_args,
                    self_path, self_repr, stdin_repr)
            except IOError:
                pass
            else:
                stream.line = int(line)
                return stream
        
    raise exception[0], exception[1], exception[2]


if __name__ == '__main__':
    input = open_input(sys.argv[1])
    print input
    print input.stream
    print input.name, '@', input.line
    input.close()
