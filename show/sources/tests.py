#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import getopt
import os
import unittest

# Internal:
import show
import viewer.compat


class CompatTest (unittest.TestCase):
    def test_stream_read_tty(self):
        master_fd, slave_fd = os.openpty()
        data = 'test data\nwith newlines'.encode()
        
        os.write(slave_fd, data)
        os.close(slave_fd)
        
        with os.fdopen(master_fd, 'rU') as stream:
            self.assertEqual(data, viewer.compat.read_stream(stream))


class OptionsTest (unittest.TestCase):
    def setUp(self):
        self.cls = show.Options
    
    
    def test_empty_args(self):
        self.assertIsInstance(self.cls.from_cmdl_args([]), self.cls)
    
    
    def test_help_opt(self):
        self.assertIsNone(self.cls.from_cmdl_args(['-h']))
    
    
    def test_unknown_opt(self):
        with self.assertRaises(getopt.GetoptError):
            self.cls.from_cmdl_args(['-|'])


if __name__ == '__main__':
    unittest.main()
