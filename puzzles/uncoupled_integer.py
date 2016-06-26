#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the only unpaired integer in a sequence of `numbers`.

Time: O(n)
Space: O(1)
"""

import sys
import unittest

def find_alone_int(numbers):

    alone = next(numbers)

    for n in numbers:
        alone ^= n

    return alone

class Test (unittest.TestCase):
    def test_single_int(self):
        self.assertEqual(
            find_alone_int((v for v in [9])),
            9)

    def test_multiple_ints(self):
        self.assertEqual(
            find_alone_int((v for v in [1, 2, 3, 4, 5, 99, 1, 2, 3, 4, 5])),
            99)

    def test_negative_ints(self):
        self.assertEqual(
            find_alone_int((v for v in [1, -123, -2, -2, 70, 1, 70])),
            -123)

if __name__ == '__main__':
    if sys.stdin.isatty():
        unittest.main(verbosity = 2)
    else:
        print(find_alone_int(map(int, sys.stdin.readline().split(', '))))
