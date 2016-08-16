#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two words are an anagram of each other.
"""

import unittest

def is_anagram(word_1, word_2):
    """
    Time: O(k+l), where k=len(word_1), l=ken(word_2)
    Space: O(k), worst-case every character is unique in word_1
    """

    # Optimization: if of different lengths, return false.

    char_count_1 = {}

    for char in word_1:
        char_count_1[char] = char_count_1.get(char, 0) + 1

    for char in word_2:
        if char not in char_count_1:
            return False

        char_count_1[char] -= 1

        if char_count_1[char] == 0:
            del char_count_1[char]

    return len(char_count_1) == 0

class Test (unittest.TestCase):
    def test_empty(self):
        self.assertTrue(is_anagram('', ''))

    def test_match(self):
        self.assertTrue(is_anagram('cat', 'act'))

    def test_same(self):
        self.assertTrue(is_anagram('cat', 'cat'))

    def test_count_mismatch(self):
        self.assertFalse(is_anagram('cart', 'cataract'))

    def test_superset(self):
        self.assertFalse(is_anagram('cart', 'cat'))

    def test_subset(self):
        self.assertFalse(is_anagram('cat', 'cart'))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
