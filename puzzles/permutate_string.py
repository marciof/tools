#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

def permutate(string):
    """
    List all permutations of `string`.

    O(n^2) where n = len(string)
    """

    if len(string) <= 1:
        return [string]

    permutations = []

    for pos, char in enumerate(string):
        substring = string[:pos] + string[pos + 1:]

        for permutation in permutate(substring):
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
