#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
List all subsets of a given set of `numbers`.

Time: O(n)
"""

import unittest

def generate(numbers):
    if len(numbers) == 0:
        return [set()]

    combs = []

    for comb in generate(numbers[1:]):
        combs.append(comb)
        combs.append({numbers[0]} | comb)

    return combs

class Test(unittest.TestCase):
    def test_many(self):
        self.assertCountEqual(
            generate([1, 2, 3]),
            [set(), {1}, {2}, {3}, {1, 2}, {2, 3}, {1, 3}, {1, 2, 3}])

    def test_empty(self):
        self.assertCountEqual(
            generate([]),
            [set()])

    def test_single(self):
        self.assertCountEqual(
            generate([1]),
            [set(), {1}])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
