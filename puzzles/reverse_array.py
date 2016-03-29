#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

def reverse(array):
    """
    Reverse an `array` in place.

    Time: O(n)
    Space: O(1)
    """

    start = 0
    end = len(array) - 1

    while start < end:
        element = array[start]
        array[start] = array[end]
        array[end] = element

        start += 1
        end -= 1

    return array

class Test (unittest.TestCase):
    def test_empty_array(self):
        array = []
        reverse(array)
        self.assertListEqual(array, [])

    def test_single_element_array(self):
        array = [1]
        reverse(array)
        self.assertListEqual(array, [1])

    def test_odd_array(self):
        array = [7, 4, 0]
        reverse(array)
        self.assertListEqual(array, [0, 4, 7])

    def test_even_array(self):
        array = [9, 5, 7, 1, 8, 8]
        reverse(array)
        self.assertListEqual(array, [8, 8, 1, 7, 5, 9])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
