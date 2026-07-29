#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Normalize a Unix-style `path`.
"""

import unittest

def normalize(path):
    stack = []

    for part in path.split('/'):
        if part == '..':
            if len(stack) > 0:
                stack.pop()
            else:
                raise ValueError('invalid path: cannot go up directory')
        elif part not in {'', '.'}:
            stack.append(part)

    new_path = '/'.join(stack)

    if path.startswith('/') and not new_path.startswith('/'):
        new_path = '/' + new_path

    if path.endswith('/') and not new_path.endswith('/'):
        if new_path == '':
            new_path = './'
        else:
            new_path += '/'

    return new_path

class Test (unittest.TestCase):
    def test_relative(self):
        self.assertEqual(normalize('a/..'), '')

    def test_relative_directory(self):
        self.assertEqual(normalize('a/../'), './')

    def test_absolute(self):
        self.assertEqual(normalize('/a/..'), '/')

    def test_absolute_directory(self):
        self.assertEqual(normalize('/a/../'), '/')

    def test_full(self):
        self.assertEqual(normalize('/a/..////b/./c/.'), '/b/c')

    def test_invalid_relative(self):
        with self.assertRaises(ValueError):
            normalize('a/../../c')

    def test_invalid_absolute(self):
        with self.assertRaises(ValueError):
            normalize('/a/../../c')

if __name__ == '__main__':
    unittest.main(verbosity = 2)
