#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import division, print_function, unicode_literals
import getopt
import unittest

# Internal:
import show as lib


class OptionsTest (unittest.TestCase):
    def test_empty_args(self):
        self.assertIsNone(lib.Options.from_argv([__name__]))
    
    
    def test_help_opt(self):
        self.assertIsNone(lib.Options.from_argv([__name__, '-h']))


    def test_unknown_opt(self):
        with self.assertRaises(getopt.GetoptError):
            lib.Options.from_argv([__name__, '-|'])


if __name__ == '__main__':
    unittest.main()
