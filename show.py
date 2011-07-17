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


class DirectoryInput (StreamInput):
    def __init__(self, path, ls_args):
        import subprocess
        
        self._process = subprocess.Popen(['ls'] + ls_args,
            stdout = subprocess.PIPE)
        
        StreamInput.__init__(self, self._process.stdout,
            name = os.path.abspath(path))
    
    
    def close(self):
        self._process.communicate()
        StreamInput.close(self)


class UriInput (StreamInput):
    def __init__(self, uri, default_protocol):
        import filelike, urlparse
        parts = urlparse.urlparse(uri)
        
        if parts.scheme == '':
            import urllib
            
            clean_uri = urllib.unquote(parts.path)
            clean_parts = urlparse.urlparse(clean_uri)
            
            if clean_parts.path == parts.path:
                uri = default_protocol + uri
            elif clean_parts.scheme == '':
                uri = default_protocol + clean_uri
            else:
                uri = clean_uri
        
        StreamInput.__init__(self, filelike.open(uri), name = uri)


def open_input(path,
        default_protocol = 'http://',
        ls_args = sys.argv[1:],
        stdin_repr = '-'):
    
    try:
        return FileInput(path)
    except IOError as error:
        if error.errno == errno.EISDIR:
            return DirectoryInput(path, ls_args)
        elif error.errno == errno.ENOENT:
            if path == stdin_repr:
                return StreamInput(sys.stdin, name = stdin_repr)
            else:
                return UriInput(path, default_protocol)
        else:
            raise


if __name__ == '__main__':
    input = open_input(sys.argv[1])
    print 'name:', input.name
    input.close()
