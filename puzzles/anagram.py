#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two words are an anagram of each other.
"""

import unittest

def is_anagram(word_a, word_b):
    char_count_a = {}

    for char in word_a:
        if char in char_count_a:
            char_count_a[char] += 1
        else:
            char_count_a[char] = 1

    for char in word_b:
        if char not in char_count_a:
            return False

        if char_count_a[char] == 1:
            del char_count_a[char]
        else:
            char_count_a[char] -= 1

    return len(char_count_a) == 0

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
