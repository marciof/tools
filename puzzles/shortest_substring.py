#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the shortest substring in `string` that contains all letters from
`alphabet` at least once.

Time: O(n)
"""

import unittest

def find_substring(string, alphabet):
    char_to_last_pos = {}
    start_char = None
    end_char = None

    for pos, char in enumerate(string):
        if char in alphabet:
            char_to_last_pos[char] = pos

            start_char = min(start_char, end_char, char,
                key = lambda c: char_to_last_pos.get(c, float('+inf')))

            end_char = max(end_char, start_char, char,
                key = lambda c: char_to_last_pos.get(c, float('-inf')))

            if len(char_to_last_pos) == len(alphabet):
                start_pos = char_to_last_pos[start_char]
                end_pos = char_to_last_pos[end_char]

                return string[start_pos : end_pos + 1]

    return None

class Test (unittest.TestCase):
    def test_repeats(self):
        self.assertEqual(
            find_substring('aabbaadca', set('abcd')),
            'baadc')

    def test_empty_string(self):
        self.assertEqual(
            find_substring('', set('abc')),
            None)

    def test_empty_alphabet(self):
        self.assertEqual(
            find_substring('hello', set()),
            None)

    def test_incomplete_alphabet(self):
        self.assertEqual(
            find_substring('world', set('rd')),
            'rld')

if __name__ == '__main__':
    unittest.main(verbosity = 2)
