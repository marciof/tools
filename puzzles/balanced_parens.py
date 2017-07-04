#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
List all possible balanced parenthesis combinations up to `total` pairs.
"""

import unittest

def permutate(total, num_open = 0, num_closed = 0):
    """
    Time: O(2^n), two branches of recursive calls for each call
    Space: O(2^n)
    """

    combinations = []

    if num_open < total:
        for c in permutate(total, num_open + 1, num_closed):
            combinations.append('(' + c)

    if num_closed < num_open:
        for c in permutate(total, num_open, num_closed + 1):
            combinations.append(')' + c)
        else:
            if (num_closed + 1) == total:
                combinations.append(')')

    return combinations

class Test (unittest.TestCase):
    def test_count_0(self):
        self.assertCountEqual(permutate(0), [])

    def test_count_1(self):
        self.assertCountEqual(permutate(1), ['()'])

    def test_count_2(self):
        self.assertCountEqual(
            permutate(2),
            [
                '()()',
                '(())',
            ])

    def test_count_3(self):
        self.assertCountEqual(
            permutate(3),
            [
                '()()()',
                '((()))',
                '(()())',
                '(())()',
                '()(())',
            ])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
