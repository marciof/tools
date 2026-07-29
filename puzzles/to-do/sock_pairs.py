#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Count the number of sock pairs with matching colors.
Sock colors are represented as integers.

Time: O(n)
"""

from typing import List, Set
import unittest


def count_sock_pairs(sock_colors: List[int]) -> int:
    num_pairs = 0
    colors_seen: Set[int] = set()

    for color in sock_colors:
        if color in colors_seen:
            num_pairs += 1
            colors_seen.remove(color)
        else:
            colors_seen.add(color)

    return num_pairs


class Test (unittest.TestCase):
    def test_no_socks(self):
        self.assertEqual(count_sock_pairs([]), 0)

    def test_single_sock(self):
        self.assertEqual(count_sock_pairs([1]), 0)

    def test_no_sock_pairs(self):
        self.assertEqual(count_sock_pairs([1, 2, 3]), 0)

    def test_all_sock_pairs(self):
        self.assertEqual(count_sock_pairs([1, 2, 3, 1, 2, 3]), 3)

    def test_missing_sock_pairs(self):
        self.assertEqual(count_sock_pairs([1, 2, 2, 3, 4, 4, 4]), 2)


if __name__ == '__main__':
    unittest.main(verbosity = 2)
