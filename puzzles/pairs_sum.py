#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find all pairs from `numbers` that when added equal `total`.

Time: O(n)
"""

import unittest

def list_pairs(numbers, total):
    needed_numbers = set()
    pairs = []

    for n in numbers:
        if n in needed_numbers:
            pairs.append((total - n, n))
        else:
            needed_numbers.add(total - n)
    
    return pairs

class Test (unittest.TestCase):
    def test_no_numbers(self):
        self.assertEqual(list_pairs([], 0), [])
    
    def test_one_number(self):
        self.assertEqual(list_pairs([1], 0), [])
    
    def test_multiple_pairs_found(self):
        self.assertEqual(
            list_pairs([2, 0, 4, 3, 9, -1, 7, 1], 3),
            [(0, 3), (4, -1), (2, 1)])
    
    def test_repeats(self):
        self.assertEqual(
            list_pairs([0, 0, 0], 0),
            [(0, 0), (0, 0)])
    
    def test_no_pairs_found(self):
        self.assertEqual(list_pairs([1, 2, 3], -1), [])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
