#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the only two integers that appear an odd number of times in a sequence of
`integers`.

Time: O(n)
Space: O(1)
"""

import unittest

def find(integers):
    """
    https://www.careercup.com/question?id=16306671#commentThread16306671

    How does this work?

    In the XOR'ed result of all numbers, by definition, any bit that is set
    is different in both of the two numbers. That means each one of
    those two can be found by XOR'ing all numbers that have that bit set,
    and all numbers that have that bit cleared.
    """

    x_y_xor = 0

    for n in integers:
        x_y_xor ^= n

    set_bit_mask = 1

    while (x_y_xor & set_bit_mask) == 0:
        set_bit_mask <<= 1

    x = 0
    y = 0

    for n in integers:
        if (n & set_bit_mask) == 0:
            x ^= n
        else:
            y ^= n

    return {x, y}

class Test (unittest.TestCase):
    def test_only_two(self):
        self.assertEqual(
            find([1, 2]),
            {1, 2})

    def test_repeated(self):
        self.assertEqual(
            find([1, 2, 3, 1, 1, 4, 1, 3, 3, 4]),
            {2, 3})

if __name__ == '__main__':
    unittest.main(verbosity = 2)
