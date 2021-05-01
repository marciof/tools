#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Rotate a square matrix 90 degrees clockwise.
"""

from typing import List
import unittest


def rotate_matrix(matrix: List[List]) -> List[List]:
    """
    Time: O(n), where n=number of elements in matrix
    Space: O(n), ditto
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


ROW_KIND = 0
COL_KIND = 1

RIGHT_DIR = [0, +1]
LEFT_DIR = [0, -1]
DOWN_DIR = [+1, 0]
UP_DIR = [-1, 0]


def should_change_direction(row_idx, col_idx, side_length) -> bool:
    max_idx = side_length - 1

    if (row_idx == 0) and (col_idx == max_idx):
        return True

    if (row_idx == max_idx) and (col_idx == max_idx):
        return True

    if (row_idx == max_idx) and (col_idx == 0):
        return True

    if (row_idx == 0) and (col_idx == 0):
        return True

    return False


def rotate_matrix_in_place(matrix: List[List]) -> List[List]:
    """
    Time: O(n), where n=number of elements in matrix
    Space: O(1)
    """

    side_length = len(matrix)

    if side_length <= 1:
        return matrix

    directions = [RIGHT_DIR, DOWN_DIR, LEFT_DIR, UP_DIR]

    src_dir_idx = directions.index(RIGHT_DIR)
    src_row_idx = 0
    src_col_idx = 0

    dest_dir_idx = directions.index(DOWN_DIR)
    dest_row_idx = 0
    dest_col_idx = side_length - 1

    for step in range(2 * side_length + 2 * (side_length - 2)):
        src_value = matrix[src_row_idx][src_col_idx]
        dest_value = matrix[dest_row_idx][dest_col_idx]

        print(src_value, dest_value)

        src_dir = directions[src_dir_idx]
        src_row_idx += src_dir[ROW_KIND]
        src_col_idx += src_dir[COL_KIND]

        dest_dir = directions[dest_dir_idx]
        dest_row_idx += dest_dir[ROW_KIND]
        dest_col_idx += dest_dir[COL_KIND]

        if should_change_direction(src_row_idx, src_col_idx, side_length):
            src_dir_idx = (src_dir_idx + 1) % len(directions)
        if should_change_direction(dest_row_idx, dest_col_idx, side_length):
            dest_dir_idx = (dest_dir_idx + 1) % len(directions)

    return []


class Test (unittest.TestCase):
    rotate_impls = {
        rotate_matrix,
        # rotate_matrix_in_place,
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
    # unittest.main(verbosity=2)
    rotate_matrix_in_place([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ])
