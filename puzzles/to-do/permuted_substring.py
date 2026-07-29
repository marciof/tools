#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find whether a `string` has any permutation of another `substring`.
"""

import unittest

def match_permutation(string, sub, pos):
    if sub == '':
        return True

    if pos >= len(string):
        return False

    for i, char in enumerate(sub):
        if char == string[pos]:
            return match_permutation(string, sub[:i] + sub[i + 1:], pos + 1)

    return False

def has_permutation(string, substring):
    if len(substring) > len(string):
        return False

    for i in range(len(string) - len(substring) + 1):
        if match_permutation(string, substring, i):
            return True

    return False

class Test (unittest.TestCase):
    def test_empty_substring(self):
        self.assertTrue(has_permutation('abca', ''))

    def test_empty_string(self):
        self.assertFalse(has_permutation('', 'abca'))

    def test_full_ordered_match(self):
        self.assertTrue(has_permutation('abca', 'abca'))

    def test_full_unordered_match(self):
        self.assertTrue(has_permutation('acab', 'abca'))

    def test_subtring_ordered_match(self):
        self.assertTrue(has_permutation('dbcfabcag', 'abca'))

    def test_subtring_unordered_match(self):
        self.assertTrue(has_permutation('dbcfaabcg', 'abca'))

    def test_dups_suffix_match(self):
        self.assertTrue(has_permutation('aaab', 'aba'))

    def test_dups_prefix_match(self):
        self.assertTrue(has_permutation('abbb', 'bab'))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
