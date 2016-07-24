#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the only unpaired integer in a sequence of `integers`.

Time: O(n)
Space: O(1)
"""

import sys
import unittest

def find(integers):
    target = 0

    for n in integers:
        target ^= n

    return target

class Test (unittest.TestCase):
    def test_single_int(self):
        self.assertEqual(
            find([9]),
            9)

    def test_multiple_ints(self):
        self.assertEqual(
            find([1, 2, 3, 4, 5, 99, 1, 2, 3, 4, 5]),
            99)

    def test_negative_ints(self):
        self.assertEqual(
            find([1, -123, -2, -2, 70, 1, 70]),
            -123)

if __name__ == '__main__':
    if sys.stdin.isatty():
        unittest.main(verbosity = 2)
    else:
        print(find(map(int, sys.stdin.readline().split(', '))))
