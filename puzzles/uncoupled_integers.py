#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the only two integers that appear an odd number of times
in a sequence of `integers`.
"""

import unittest

def find(integers):
    """
    Time: O(n)
    Space: O(1)

    https://www.careercup.com/question?id=16306671#commentThread16306671
    """

    x_y_xor = 0

    for n in integers:
        x_y_xor ^= n

    bit_mask = 1

    while (x_y_xor & bit_mask) == 0:
        bit_mask <<= 1

    x = 0
    y = 0

    for n in integers:
        if (n & bit_mask) == 0:
            x ^= n
        else:
            y ^= n

    return {x, y}

class Test (unittest.TestCase):
    def test_only_two(self):
        self.assertEqual(
            find([3, 0]),
            {3, 0})

    def test_repeated(self):
        self.assertEqual(
            find([1, -2, 3, 1, 1, 4, 1, 3, 3, 4]),
            {-2, 3})

if __name__ == '__main__':
    unittest.main(verbosity = 2)
