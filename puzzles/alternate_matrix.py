#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Read the rows of a matrix (as a 2D array) alternatively from right to left,
left to right, and so on, and return them as a 1D array.

Time: O(n)
"""

import unittest

def transform_simple(matrix):
    is_reversed = False
    array = []

    for row in matrix:
        array.extend(reversed(row) if is_reversed else row)
        is_reversed = not is_reversed

    return array

def transform_manual(matrix):
    is_reversed = False
    array = []

    for row in matrix:
        if is_reversed:
            start = len(row) - 1
            stop = -1
            step = -1
        else:
            start = 0
            stop = len(row)
            step = +1

        for i in range(start, stop, step):
            array.append(row[i])

        is_reversed = not is_reversed

    return array

class TestSuite:
    def test_square_matrix(self):
        self.assertEqual(
            self.transform([
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ]),
            [1, 2, 3, 6, 5, 4, 7, 8, 9])

    def test_rectangular_matrix(self):
        self.assertEqual(
            self.transform([
                ['a', 'b'],
                ['c', 'd'],
                ['e', 'f'],
                ['g', 'h'],
            ]),
            ['a', 'b', 'd', 'c', 'e', 'f', 'h', 'g'])

    def test_single_element_matrix(self):
        self.assertEqual(self.transform([[100]]), [100])

    def test_empty_matrix(self):
        self.assertEqual(self.transform([]), [])

class TestSimple (unittest.TestCase, TestSuite):
    def transform(self, *args):
        return transform_simple(*args)

class TestManual (unittest.TestCase, TestSuite):
    def transform(self, *args):
        return transform_manual(*args)

if __name__ == '__main__':
    unittest.main(verbosity = 2)
