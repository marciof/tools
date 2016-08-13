#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two strings have an identical character set.
"""

import unittest

def has_same_char_set(str_a, str_b):
    char_set_a = set()
    char_set_b = set()

    for char in str_a:
        char_set_a.add(char)

    for char in str_b:
        if char not in char_set_a:
            return False

        char_set_b.add(char)

    return len(char_set_a) == len(char_set_b)

class Test (unittest.TestCase):
    def test_empty(self):
        self.assertTrue(has_same_char_set('', ''))

    def test_superset(self):
        self.assertFalse(has_same_char_set('aabc', 'bcb'))

    def test_subset(self):
        self.assertFalse(has_same_char_set('bcb', 'aabc'))

    def test_same(self):
        self.assertTrue(has_same_char_set('abaacab', 'abc'))

    def test_mix(self):
        self.assertFalse(has_same_char_set('abaacab', 'ddcbd'))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
