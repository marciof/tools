#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

def permutate(total, combination = '', nr_open = 0, nr_closed = 0):
    """
    List all possible balanced parenthesis combinations up to `total` pairs.

    At any point there are two options: print an open parenthesis if available
    and check recursively for a solution, print a closed parenthesis if a
    corresponding open parenthesis has been printed and check recursively for a
    solution.

    Time: O(n)
    """

    combinations = []

    if (nr_open == total) and (nr_closed == total):
        combinations.append(combination)
    else:
        if nr_open < total:
            combinations.extend(
                permutate(total, combination + '(', nr_open + 1, nr_closed))

        if nr_closed < nr_open:
            combinations.extend(
                permutate(total, combination + ')', nr_open, nr_closed + 1))

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
