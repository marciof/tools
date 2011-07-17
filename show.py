#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard library:
from __future__ import unicode_literals
import errno, os, sys


# NOTE: No abstract base class for performance.
class StreamInput:
    def __init__(self, stream, name):
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
            raise Exception()
        
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
        stdin_repr = '-'):
    
    try:
        return FileInput(path)
    except IOError as error:
        exception = sys.exc_info()
        
        if error.errno == errno.EISDIR:
            return DirectoryInput(path, ls_args)
        elif error.errno == errno.ENOENT:
            if path == stdin_repr:
                return StreamInput(sys.stdin, name = stdin_repr)
            
            try:
                return PerlDocInput(path)
            except Exception:
                pass
            
            try:
                return PyDocInput(path)
            except Exception:
                pass
            
            try:
                return UriInput(path, default_protocol)
            except IOError as uri_error:
                if uri_error.filename is not None:
                    return open_input(uri_error.filename,
                        default_protocol, ls_args, stdin_repr)
            
            raise exception[0], exception[1], exception[2]
        else:
            raise


if __name__ == '__main__':
    input = open_input(sys.argv[1])
    print input, input.name
    input.close()
