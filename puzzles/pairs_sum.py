#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find all pairs from `numbers` that when added equal `total`.

Time: O(n)
"""

import bisect
import math
import unittest

def list_pairs_functional(numbers, total):
    needed_nrs = set()
    pairs = []

    for n in numbers:
        target = total - n

        if n in needed_nrs:
            pairs.append((n, target))
        else:
            needed_nrs.add(target)
    
    return pairs

def list_pairs_in_place(numbers, total):
    numbers.sort()
    pairs = []

    for i in range(0, math.ceil(len(numbers))):
        n = numbers[i]
        target = total - n
        j = bisect.bisect_left(numbers, target, i + 1)

        if (j < len(numbers)) and (numbers[j] == target):
            pairs.append((n, target))

    return pairs

def normalize(pairs):
    return sorted(map(sorted, pairs))

class TestSuite:
    def test_no_numbers(self):
        self.assertEqual(self.list_pairs([], 0), [])
    
    def test_one_number(self):
        self.assertEqual(self.list_pairs([1], 0), [])
    
    def test_multiple_pairs_found(self):
        self.assertEqual(
            normalize(self.list_pairs([2, 0, 4, 3, 9, -1, 7, 1], 3)),
            normalize([(0, 3), (4, -1), (2, 1)]))
    
    def test_repeats(self):
        self.assertEqual(
            normalize(self.list_pairs([0, 0, 0], 0)),
            normalize([(0, 0), (0, 0)]))
    
    def test_no_pairs_found(self):
        self.assertEqual(self.list_pairs([1, 2, 3], -1), [])

class TestFunctional (unittest.TestCase, TestSuite):
    def list_pairs(self, *args):
        return list_pairs_functional(*args)

class TestInPlace (unittest.TestCase, TestSuite):
    def list_pairs(self, *args):
        return list_pairs_in_place(*args)

if __name__ == '__main__':
    unittest.main(verbosity = 2)
