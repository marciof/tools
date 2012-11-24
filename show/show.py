#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
Universal viewer.
"""


# Standard:
from __future__ import unicode_literals
import sys


class Options:
    def parse(self, argv):
        # argparse isn't used for performance.
        import getopt
        
        (options, arguments) = getopt.getopt(argv[1:], 'h')
        
        for option, value in options:
            if option == '-h':
                print 'Universal viewer.'
                return False


if __name__ == '__main__':
    if not Options().parse(sys.argv):
        sys.exit()
