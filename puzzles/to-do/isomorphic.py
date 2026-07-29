#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two words are isomorphic.
"""

import unittest

def is_isomorphic(word_1, word_2):
    """
    Time: O(n), where n=len(word_1)=len(word_2
    Space: O(n)
    """

    if len(word_1) != len(word_2):
        return False

    char_map_1 = {}
    char_map_2 = {}

    for char_1, char_2 in zip(word_1, word_2):

        if char_1 not in char_map_1:
            char_map_1[char_1] = char_2
        elif char_map_1[char_1] != char_2:
            return False

        if char_2 not in char_map_2:
            char_map_2[char_2] = char_1
        elif char_map_2[char_2] != char_1:
            return False

    return True

class Test (unittest.TestCase):
    def test_empty(self):
        self.assertTrue(is_isomorphic('', ''))

    def test_different_lengths(self):
        self.assertFalse(is_isomorphic('loo', 'appt'))

    def test_mismatch(self):
        self.assertFalse(is_isomorphic('loo', 'doa'))
        self.assertFalse(is_isomorphic('doa', 'loo'))

    def test_isomorphic(self):
        self.assertTrue(is_isomorphic('aba', 'cac'))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
