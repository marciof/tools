#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest


def find_substring(string, alphabet):
    """
    Find the shortest substring in `string` that contains all letters from
    `alphabet` at least once.
    """
    
    last_pos_by_char = {}
    start_char = None
    end_char = None
    
    for char, pos in zip(string, range(len(string))):
        if len(last_pos_by_char) == len(alphabet):
            break
        
        if char not in alphabet:
            continue
        
        last_pos_by_char[char] = pos
        
        start_char = min(start_char, end_char, char,
            key = lambda c: last_pos_by_char.get(c, float('+inf')))
        
        end_char = max(end_char, start_char, char,
            key = lambda c: last_pos_by_char.get(c, float('-inf')))
    
    if None in (start_char, end_char):
        return None
    else:
        start = last_pos_by_char[start_char]
        end = last_pos_by_char[end_char]
        return string[start : end + 1]


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
