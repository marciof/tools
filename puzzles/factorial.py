#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Calculate the factorial of `n`.

Time: O(n)
"""

import sys
import unittest

def calculate(n, result = 1):
    if n <= 1:
        return result
    else:
        return calculate(n - 1, n * result)

class Test (unittest.TestCase):
    def test_for_0(self):
        self.assertEqual(calculate(0), 1)

    def test_for_1(self):
        self.assertEqual(calculate(1), 1)

    def test_for_3(self):
        self.assertEqual(calculate(3), 6)

    def test_for_7(self):
        self.assertEqual(calculate(7), 5040)

if __name__ == '__main__':
    if sys.stdin.isatty():
        unittest.main(verbosity = 2)
    else:
        print(calculate(int(sys.stdin.readline())))
