#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Calculate the `n`-th value of the Fibonacci sequence.

Time: O(n)
Memory: O(1)
"""

import sys
import unittest

def calculate(n, result = 0, nxt = 1):
    if n == 0:
        return result
    else:
        return calculate(n - 1, nxt, nxt + result)

class Test (unittest.TestCase):
    def test_for_0(self):
        self.assertEqual(calculate(0), 0)

    def test_for_1(self):
        self.assertEqual(calculate(1), 1)

    def test_for_4(self):
        self.assertEqual(calculate(4), 3)

    def test_for_12(self):
        self.assertEqual(calculate(12), 144)

    def test_for_30(self):
        self.assertEqual(calculate(30), 832040)

if __name__ == '__main__':
    if sys.stdin.isatty():
        unittest.main(verbosity = 2)
    else:
        print(calculate(int(sys.stdin.readline())))
