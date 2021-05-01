#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Rotate a square matrix 90 degrees clockwise.
"""

from collections import namedtuple
from typing import List, Tuple
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


Direction = namedtuple('Direction', ['row', 'col'])

RIGHT_DIR = Direction(row=0, col=+1)
LEFT_DIR = Direction(row=0, col=-1)
DOWN_DIR = Direction(row=+1, col=0)
UP_DIR = Direction(row=-1, col=0)

CLOCKWISE_DIRS = (RIGHT_DIR, DOWN_DIR, LEFT_DIR, UP_DIR)


def rotate_clockwise(
        row: int, col: int, dir: Direction, side_len: int) -> Tuple[int, int]:

    steps = side_len - 1
    to_row = row + steps * dir.row
    to_col = col + steps * dir.col

    if (to_row > steps) or (to_row < 0) or (to_col > steps) or (to_col < 0):
        excess_row = abs(to_row) % steps
        excess_col = abs(to_col) % steps
        excess = max(excess_row, excess_col)

        dir_idx = CLOCKWISE_DIRS.index(dir)
        to_dir: Direction = CLOCKWISE_DIRS[(dir_idx + 1) % len(CLOCKWISE_DIRS)]

        row_sign = -1 if to_row < 0 else +1
        col_sign = -1 if to_col < 0 else +1

        to_row += -(row_sign * excess_row) + (excess * to_dir.row)
        to_col += -(col_sign * excess_col) + (excess * to_dir.col)

    return (to_row, to_col)


def rotate_matrix_in_place(matrix: List[List]) -> List[List]:
    side_length = len(matrix)
    offset = 0

    while side_length >= 2:
        for col in range(offset, offset + side_length - 1):
            row = offset
            dir = RIGHT_DIR
            dir_idx = CLOCKWISE_DIRS.index(dir)

            print('---')

            for step in range(4):
                print(row, col, matrix[row][col])
                (row, col) = rotate_clockwise(row, col, dir, side_length)
                dir = CLOCKWISE_DIRS[(dir_idx + 1) % len(CLOCKWISE_DIRS)]
                dir_idx += 1

        side_length -= 2
        offset += 1

    return matrix


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
    # unittest.main(verbosity=2)
    # rotate_matrix_in_place([
    #     [1, 2],
    #     [3, 4],
    # ])

    # rotate_matrix_in_place([
    #     [1, 2, 3],
    #     [4, 5, 6],
    #     [7, 8, 9],
    # ])

    rotate_matrix_in_place([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
    ])
