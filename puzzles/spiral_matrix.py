#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Create a clock-wise spiral starting at the center of a square matrix of
side length `size` with consecutive positive integers.
"""

import collections
import unittest

Direction = collections.namedtuple('Direction', ['x', 'y'])

UP = Direction(x = 0, y = -1)
DOWN = Direction(x = 0, y = +1)
LEFT = Direction(x = -1, y = 0)
RIGHT = Direction(x = +1, y = 0)

def create_spiral(size):
    clockwise_direction = [UP, RIGHT, DOWN, LEFT]
    matrix = [[0] * size for _ in range(size)]
    x = y = int((size - 1) / 2)
    curr_direction = 0
    nr_sides_so_far = 0
    side_length_so_far = 0
    max_side_length = 1
    nr = 1

    while (y >= 0) and (x >= 0) and (y < size) and (x < size):
        matrix[y][x] = nr
        nr += 1
        side_length_so_far += 1

        if side_length_so_far == max_side_length:
            nr_sides_so_far += 1
            side_length_so_far = 0
            curr_direction = (curr_direction + 1) % len(clockwise_direction)

        if nr_sides_so_far < 4:
            x += clockwise_direction[curr_direction].x
            y += clockwise_direction[curr_direction].y
        else:
            x += clockwise_direction[-1].x
            y += clockwise_direction[-1].y

            nr_sides_so_far = 0
            max_side_length += 2

    return matrix

class Test (unittest.TestCase):
    def test_empty(self):
        self.assertEqual(create_spiral(0), [])

    def test_size_1(self):
        self.assertEqual(create_spiral(1), [[1]])

    def test_even_size(self):
        self.assertEqual(
            create_spiral(4),
            [
                [ 7,  8,  9, 10],
                [ 6,  1,  2, 11],
                [ 5,  4,  3, 12],
                [16, 15, 14, 13]
            ])

    def test_odd_size(self):
        self.assertEqual(
            create_spiral(3),
            [
                [7, 8, 9],
                [6, 1, 2],
                [5, 4, 3]
            ])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
