#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the first character that doesn't repeat anywhere else in a `string`.
"""

import unittest

def find_char(string):
    """
    Space: O(n)
    Time: O(n)
    """

    seen_chars = set()
    char_to_first_pos = {}

    for pos, char in enumerate(string):
        if char in seen_chars:
            char_to_first_pos.pop(char, None)
        else:
            seen_chars.add(char)
            char_to_first_pos[char] = pos

    target_pos = min(char_to_first_pos.values(), default = None)

    if target_pos is not None:
        return string[target_pos]

class Test (unittest.TestCase):
    def test_empty_string(self):
        self.assertIsNone(find_char(''))

    def test_single_char(self):
        self.assertEqual(find_char('a'), 'a')

    def test_all_dups(self):
        self.assertIsNone(find_char('bbbbbbb'))

    def test_no_dups(self):
        self.assertEqual(find_char('qwertyuiop'), 'q')

    def test_mix(self):
        self.assertEqual(find_char('abdbcace'), 'd')

if __name__ == '__main__':
    unittest.main(verbosity = 2)
