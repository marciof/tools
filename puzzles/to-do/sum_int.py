#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Sum two integers without using `+` and `-`.
"""

import unittest

def add(a, b, bits = 32):
    """
    http://stackoverflow.com/a/1150996/753501
    https://discuss.leetcode.com/topic/49900/python-solution
    """

    mask = 0
    for i in range(0, bits):
        mask = (mask << 1) | 1

    max_limit = mask >> 1
    min_limit = 1 << (bits - 1)

    while b != 0:
        # result w/o carry: 0+0=0, 0+1=1+0=1, 1+1=0
        # carry: 1+1=2
        a, b = (a ^ b) & mask, ((a & b) << 1) & mask

    if a <= max_limit:
        return a
    else:
        return (a % min_limit) - min_limit

class Test (unittest.TestCase):
    def test_positive_with_positive(self):
        self.assertEqual(add(1, 3), 4)

    def test_positive_with_negative(self):
        self.assertEqual(add(1, -1), 0)
        self.assertEqual(add(2147483647, -2147483648), -1)

    def test_negative_with_negative(self):
        self.assertEqual(add(-12, -8), -20)

if __name__ == '__main__':
    unittest.main(verbosity = 2)
