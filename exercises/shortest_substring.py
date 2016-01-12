#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Standard:
from __future__ import absolute_import, division, unicode_literals
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
    def test_simple(self):
        self.assertEquals(
            find_substring('aabbaadca', set('abcd')),
            'baadc')


if __name__ == '__main__':
    unittest.main(verbosity = 2)
