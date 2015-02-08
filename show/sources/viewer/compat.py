# -*- coding: UTF-8 -*-


# Standard:
import sys


# http://bugs.python.org/issue5380
if sys.version_info < (2, 7):
    read_stream = file.read
else:
    # Standard:
    import errno
    
    def read_stream(stream):
        """
        :type stream: file
        """
        
        if not stream.isatty():
            return stream.read()
        
        output = bytearray()
        
        try:
            byte = stream.read(1)
            
            if byte != '':
                output.append(byte)
                
                while byte != '':
                    byte = stream.read(1)
                    output.append(byte)
        except IOError as error:
            if error.errno != errno.EIO:
                raise
        
        return output
