#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
List all possible balanced parenthesis combinations up to `total` pairs.

At any point there are two options: print an open parenthesis if available
and check recursively for a solution, print a closed parenthesis if a
corresponding open parenthesis has been printed and check recursively for a
solution.

Time: O(n)
"""

import unittest

def permutate(total, nr_open = 0, nr_closed = 0):
    combinations = []

    if nr_open == nr_closed == total:
        combinations.append('')
    else:
        if nr_open < total:
            for c in permutate(total, nr_open + 1, nr_closed):
                combinations.append('(' + c)

        if nr_closed < nr_open:
            for c in permutate(total, nr_open, nr_closed + 1):
                combinations.append(')' + c)

    return combinations

class Test(unittest.TestCase):
    def test_count_1(self):
        self.assertCountEqual(
            permutate(1),
            ['()'])

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
