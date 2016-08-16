#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
List all possible balanced parenthesis combinations up to `total` pairs.
"""

import unittest

def permutate(total, nr_open = 0, nr_closed = 0):
    """
    Time: O(2^n), two branches of recursive calls for each call
    Space: O(2^n)
    """

    combinations = []

    if nr_open < total:
        for c in permutate(total, nr_open + 1, nr_closed):
            combinations.append('(' + c)

    if nr_closed < nr_open:
        for c in permutate(total, nr_open, nr_closed + 1):
            combinations.append(')' + c)
        else:
            if (nr_closed + 1) == total:
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
