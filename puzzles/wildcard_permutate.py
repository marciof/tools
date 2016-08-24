#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Generate all combinations of the `pattern` string, consisting of `'0'` and
`'1'`, where `'?'` is a wildcard.
"""

import unittest

def generate(pattern):
    """
    Time: O(n)
    Space: O(n.2^k), where n=len(pattern), k=number of wildcards
    """

    if pattern == '':
        return ['']

    if pattern[0] == '?':
        prefixes = {'0', '1'}
    else:
        prefixes = {pattern[0]}

    combinations = []

    for combination in generate(pattern[1:]):
        for prefix in prefixes:
            combinations.append(prefix + combination)

    return combinations

class Test (unittest.TestCase):
    def test_fixed_string(self):
        self.assertCountEqual(
            generate('01101'),
            {'01101'})

    def test_single_wildcard(self):
        self.assertCountEqual(
            generate('011?0'),
            {'01100', '01110'})

    def test_multiple_wildcard(self):
        self.assertCountEqual(
            generate('011?0?'),
            {'011000', '011100', '011001', '011101'})

    def test_empty_string(self):
        self.assertCountEqual(
            generate(''),
            {''})

    def test_wildcard_string(self):
        self.assertCountEqual(
            generate('??'),
            {'00', '01', '10', '11'})

if __name__ == '__main__':
    unittest.main(verbosity = 2)
