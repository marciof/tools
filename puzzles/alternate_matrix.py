#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Read the rows of a matrix (as a 2D array) alternatively from left to right,
right to left, and so on, and return them as a 1D array.

Time: O(n)
"""

from typing import List
import unittest


def transform_simple(matrix: List[List]) -> List:
    array = []
    is_reversed = False

    for row in matrix:
        array.extend(reversed(row) if is_reversed else row)
        is_reversed = not is_reversed

    return array


def transform_iter(matrix: List[List]) -> List:
    is_reversed = False

    for row in matrix:
        if is_reversed:
            yield from reversed(row)
        else:
            yield from row

        is_reversed = not is_reversed


def transform_manual(matrix: List[List]) -> List:
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


class Test (unittest.TestCase):
    transform_iter_list = lambda matrix: list(transform_iter(matrix))

    transform_impls = (
        transform_simple,
        transform_manual,
        transform_iter_list,
    )

    def test_square_matrix(self):
        for transform in self.transform_impls:
            with self.subTest(transform):
                self.assertEqual(
                    transform([
                        [1, 2, 3],
                        [4, 5, 6],
                        [7, 8, 9]
                    ]),
                    [1, 2, 3, 6, 5, 4, 7, 8, 9])

    def test_rectangular_matrix(self):
        for transform in self.transform_impls:
            with self.subTest(transform):
                self.assertEqual(
                    transform([
                        ['a', 'b'],
                        ['c', 'd'],
                        ['e', 'f'],
                        ['g', 'h'],
                    ]),
                    ['a', 'b', 'd', 'c', 'e', 'f', 'h', 'g'])

    def test_single_element_matrix(self):
        for transform in self.transform_impls:
            with self.subTest(transform):
                self.assertEqual(transform([[100]]), [100])

    def test_empty_matrix(self):
        for transform in self.transform_impls:
            with self.subTest(transform):
                self.assertEqual(transform([]), [])


if __name__ == '__main__':
    unittest.main(verbosity = 2)
