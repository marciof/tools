#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two strings have an identical character set.
"""

import unittest

def has_same_char_set(str_1, str_2):
    """
    Time: O(k+l), where k=len(str_1), l=len(str_2)
    Space: O(k+l), worst-case every character is unique in both strings
    """

    char_set_1 = set()
    char_set_2 = set()

    for char in str_1:
        char_set_1.add(char)

    for char in str_2:
        if char not in char_set_1:
            return False

        char_set_2.add(char)

    return len(char_set_1) == len(char_set_2)

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
