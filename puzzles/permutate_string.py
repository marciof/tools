#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
List all permutations of `string`.

Time: O(n^2) where n = len(string)
"""

import unittest

def permutate(string):
    if string == '':
        return ['']

    permutations = []

    for i, char in enumerate(string):
        for permutation in permutate(string[:i] + string[i + 1:]):
            permutations.append(char + permutation)

    return permutations

class Test (unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(permutate(''), [''])

    def test_single_char_string(self):
        self.assertEqual(permutate('a'), ['a'])

    def test_unique_chars_string(self):
        self.assertCountEqual(permutate('abc'), [
            'abc',
            'acb',
            'bac',
            'bca',
            'cab',
            'cba',
        ])

    def test_repeated_chars_string(self):
        self.assertCountEqual(permutate('aab'), [
            'aab',
            'aba',
            'aab',
            'aba',
            'baa',
            'baa',
        ])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
