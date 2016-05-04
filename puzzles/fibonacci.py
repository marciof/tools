#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import unittest

def calculate(n, prev = 1, prev_prev = 0):
    """
    Calculate the `n`-th value of the Fibonacci sequence.
    """

    if n == 0:
        return prev_prev
    else:
        return calculate(n - 1, prev_prev + prev, prev)

class Test (unittest.TestCase):
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
