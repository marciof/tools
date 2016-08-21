#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the position of the first uppercase letter, in an array composed of
zero or more lowercase letters followed by zero or more uppercase letters.

Return `None` if not found.

The array size isn't known, only a function is given that returns a letter
by index or raises `IndexError` if the index is out of bounds.
"""

import unittest

def find(get_elem):
    """
    Time: O(log n), log n for upper bound + log n for binary search
    Space: O(1)
    """

    low = 1
    high = None
    middle = low
    is_upper = False

    while True:
        try:
            char = get_elem(middle - 1)
        except IndexError:
            high = middle
            is_upper = False
        else:
            if char.isupper():
                high = middle
                is_upper = True
            else:
                low = middle

        if high is None:
            middle = low * 2
        else:
            middle = low + (high - low) // 2

            if middle == low:
                break

    return high - 1 if is_upper else None

class Test (unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(find([].__getitem__))

    def test_single_lowercase(self):
        self.assertIsNone(find(['a'].__getitem__))

    def test_single_uppercase(self):
        self.assertEqual(find(['A'].__getitem__), 0)

    def test_multiple_lowercase(self):
        self.assertIsNone(find(['c', 'b', 'a'].__getitem__))

    def test_multiple_uppercase(self):
        self.assertEqual(find(['C', 'B', 'A'].__getitem__), 0)

    def test_mix(self):
        self.assertEqual(
            find(['c', 'b', 'a', 'e', 'a', 'd', 'C', 'B', 'A'].__getitem__),
            6)

if __name__ == '__main__':
    unittest.main(verbosity = 2)
