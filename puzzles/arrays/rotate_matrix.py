#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Rotate a square matrix 90 degrees clockwise.
"""

from dataclasses import dataclass
from typing import List, Tuple
import unittest


def rotate_matrix(matrix: List[List]) -> List[List]:
    """
    Time: O(n), where n=number of elements in matrix
    Space: O(n), ditto
    """

    new_matrix = []

    for column_idx in range(len(matrix)):
        row = []

        for row_idx in reversed(range(len(matrix))):
            row.append(matrix[row_idx][column_idx])

        new_matrix.append(row)

    return new_matrix


@dataclass
class Direction:
    row: int
    col: int
    next: 'Direction'


# Clockwise directions.
CW_UP_DIR = Direction(row=-1, col=0, next=None)
CW_LEFT_DIR = Direction(row=0, col=-1, next=CW_UP_DIR)
CW_DOWN_DIR = Direction(row=+1, col=0, next=CW_LEFT_DIR)
CW_RIGHT_DIR = Direction(row=0, col=+1, next=CW_DOWN_DIR)
CW_UP_DIR.next = CW_RIGHT_DIR


def rotate_clockwise(
        row: int, col: int, dir: Direction, side_len: int) -> Tuple[int, int]:

    """
    Rotate a row/column position 90 degrees clockwise, in a square matrix.
    """

    steps = side_len - 1
    to_row = row + steps * dir.row
    to_col = col + steps * dir.col

    # If the destination row or column are out of bounds, then that means
    # the direction must change.
    if (to_row > steps) or (to_row < 0) or (to_col > steps) or (to_col < 0):

        # How much out of bounds the destination row and column are indicates
        # how many steps there are left to be taken in the next clockwise
        # direction.
        excess_rows = abs(to_row) % steps
        excess_cols = abs(to_col) % steps

        # Only one axis at-a-time will ever be out of bounds (row or column).
        # Since each one of the 4-way directions always has a "null" (zero)
        # step, then whichever source (row or column) the excess steps come
        # from will then be used to step in the right direction, while
        # "zeroing" the other one.
        excess_steps = max(excess_rows, excess_cols)

        # When going left/up and out of bounds, then the row/column can get
        # negative. Get its sign to turn it non-negative.
        row_sign = -1 if to_row < 0 else +1
        col_sign = -1 if to_col < 0 else +1

        next_dir = dir.next
        to_row += -(row_sign * excess_rows) + (excess_steps * next_dir.row)
        to_col += -(col_sign * excess_cols) + (excess_steps * next_dir.col)

    return (to_row, to_col)


def rotate_matrix_in_place(matrix: List[List]) -> List[List]:
    """
    Time: O(n), where n=number of elements in matrix
    Space: O(1)
    """

    side_len = len(matrix)
    row_col_offset = 0

    # Rotate matrix in "layers", starting from the outside rows and columns
    # in increasingly smaller "inner" matrices. When the matrix side length
    # is less than 2, then it's fully rotated.
    while side_len >= 2:

        # Rotate values starting from the first row and every column.
        for col in range(row_col_offset, row_col_offset + side_len - 1):
            row = row_col_offset
            direction = CW_RIGHT_DIR
            previous_value = matrix[row][col]

            # Rotate 4 sides at-a-time only, so that no extra space is needed
            # to keep track of values to be carried over.
            for step in range(4):
                (next_row, next_col) = rotate_clockwise(
                    row, col, direction, side_len)

                next_value = matrix[next_row][next_col]
                matrix[next_row][next_col] = previous_value
                previous_value = next_value

                row = next_row
                col = next_col
                direction = direction.next

        # Go to the next smaller inner matrix. Decrease side length by two,
        # since both outside rows and columns have already been rotated above.
        side_len -= 2
        row_col_offset += 1

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

    def test_length_4_matrix(self):
        for rotate in self.rotate_impls:
            with self.subTest(rotate):
                self.assertEqual(
                    rotate([
                        [1, 2, 3, 4],
                        [5, 6, 7, 8],
                        [9, 10, 11, 12],
                        [13, 14, 15, 16],
                    ]),
                    [
                        [13, 9, 5, 1],
                        [14, 10, 6, 2],
                        [15, 11, 7, 3],
                        [16, 12, 8, 4],
                    ])


if __name__ == '__main__':
    unittest.main(verbosity=2)
