#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
Universal viewer.
"""


# No imports here, modules are loaded as needed for performance.


class Options:
    @classmethod
    def from_argv(cls, argv):
        # argparse is slower.
        import getopt # standard
        
        (options, _) = getopt.getopt(argv[1:], 'h')
        
        for option, _ in options:
            if option == '-h':
                # Cython doesn't support docstrings:
                # sys.modules[__name__].__doc__.strip()
                print 'Universal viewer.'
                return None
        
        return None


if __name__ == '__main__':
    import sys # standard
    
    if not Options.from_argv(sys.argv):
        sys.exit()
