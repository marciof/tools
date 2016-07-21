#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the first character that doesn't repeat anywhere else in a `string`.

Time: O(n)
"""

import unittest

def find_char(string):
    seen_chars = set()
    char_to_pos = {}

    for pos, char in enumerate(string):
        if char in seen_chars:
            char_to_pos.pop(char, None)
        else:
            seen_chars.add(char)
            char_to_pos[char] = pos

    target_pos = float('+inf')

    for char, pos in char_to_pos.items():
        if pos == 0:
            return char
        elif pos < target_pos:
            target_pos = pos

    if target_pos == float('+inf'):
        return None
    else:
        return string[target_pos]

class Test(unittest.TestCase):
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
