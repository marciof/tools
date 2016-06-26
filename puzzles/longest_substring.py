#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the longest substring without repeating characters.

Time: O(n)
"""

import unittest

def find_substring(string):
    if string == '':
        return ''

    best_start = 0
    best_end = -1

    start = 0
    end = -1

    char_to_pos = {}

    for i, char in enumerate(string):
        pos = char_to_pos.get(char, -1)

        if pos >= start:
            if (end - start) > (best_end - best_start):
                best_start = start
                best_end = end

            start = pos + 1

        char_to_pos[char] = i
        end = i

    if (end - start) > (best_end - best_start):
        best_start = start
        best_end = end

    return string[best_start : best_end + 1]

class Test (unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(find_substring(''), '')

    def test_single_char(self):
        self.assertEqual(find_substring('x'), 'x')

    def test_repeated_char(self):
        self.assertEqual(find_substring('yyyyyyyyyyy'), 'y')

    def test_repeated_substrings(self):
        self.assertEqual(find_substring('abcabcbb'), 'abc')

    def test_non_empty_string_1(self):
        self.assertEqual(find_substring('pwwkew'), 'wke')

    def test_non_empty_string_2(self):
        self.assertEqual(find_substring('dvdf'), 'vdf')

    def test_non_empty_string_3(self):
        self.assertEqual(find_substring('edvdfe'), 'vdfe')

if __name__ == '__main__':
    unittest.main(verbosity = 2)
