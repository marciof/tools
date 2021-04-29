#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Rotate a square matrix.
"""

from typing import List
import unittest


def rotate_matrix(matrix: List[List]) -> List[List]:
    """
    Time: O()
    Space: O()
    """

    if len(matrix) <= 1:
        return matrix

    new_matrix = []
    size = len(matrix)

    for column_idx in range(size):
        row = []

        for row_idx in reversed(range(size)):
            row.append(matrix[row_idx][column_idx])

        new_matrix.append(row)

    return new_matrix


# TODO
def rotate_matrix_in_place(matrix: List[List]) -> List[List]:
    pass


class Test (unittest.TestCase):
    rotate_impls = {
        rotate_matrix,
        rotate_matrix_in_place,
    }

    def test_empty_matrix(self):
        for rotate in self.rotate_impls:
            with self.subTest(rotate):
                self.assertEqual(rotate([]), [])

    def test_length_1_matrix(self):
        for rotate in self.rotate_impls:
            with self.subTest(rotate):
                self.assertEqual(rotate([[1]]), [[1]])

    def test_length_2_matrix(self):
        for rotate in self.rotate_impls:
            with self.subTest(rotate):
                self.assertEqual(
                    rotate([
                        [1, 2],
                        [3, 4],
                    ]),
                    [
                        [3, 1],
                        [4, 2],
                    ])

    def test_length_3_matrix(self):
        for rotate in self.rotate_impls:
            with self.subTest(rotate):
                self.assertEqual(
                    rotate([
                        [1, 2, 3],
                        [4, 5, 6],
                        [7, 8, 9],
                    ]),
                    [
                        [7, 4, 1],
                        [8, 5, 2],
                        [9, 6, 3],
                    ])


if __name__ == '__main__':
    unittest.main(verbosity=2)
