#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Checks if the last used piece of `color` at position `x` and `y` in the
`board` has won the game or not.
"""

import collections
import unittest

Direction = collections.namedtuple('Direction', ['x', 'y'])

UP = Direction(x = 0, y = +1)
DOWN = Direction(x = 0, y = -1)
LEFT = Direction(x = -1, y = 0)
RIGHT = Direction(x = +1, y = 0)

UP_LEFT = Direction(x = -1, y = +1)
UP_RIGHT = Direction(x = +1, y = +1)
DOWN_LEFT = Direction(x = -1, y = -1)
DOWN_RIGHT = Direction(x = +1, y = -1)

def is_winner(color, x, y, board, max_nr_pieces = 4):
    directions = [
        (UP, DOWN),
        (LEFT, RIGHT),
        (UP_LEFT, DOWN_RIGHT),
        (UP_RIGHT, DOWN_LEFT),
    ]

    for forward, opposite in directions:
        nr_pieces = 1

        for direction in forward, opposite:
            curr_x = x + direction.x
            curr_y = y + direction.y

            while (curr_y >= 0) \
                    and (curr_x >= 0) \
                    and (curr_y < len(board)) \
                    and (curr_x < len(board[curr_y])):

                if board[curr_y][curr_x] != color:
                    break

                nr_pieces += 1
                curr_x += direction.x
                curr_y += direction.y

                if nr_pieces >= max_nr_pieces:
                    return True

    return False

class Test (unittest.TestCase):
    def test_empty_board(self):
        self.assertFalse(is_winner(color = 1, x = 0, y = 4, board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]))

    def test_no_winner_close_to_boundary(self):
        self.assertFalse(is_winner(color = 1, x = 2, y = 4, board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [1, 1, 1, 2, 2],
        ]))

    def test_winner_horizontal(self):
        self.assertTrue(is_winner(color = 1, x = 2, y = 4, board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 1, 1, 1, 1],
        ]))

    def test_winner_diagonal(self):
        self.assertTrue(is_winner(color = 1, x = 3, y = 2, board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 1, 2],
            [0, 0, 1, 1, 2],
            [2, 1, 2, 1, 2],
        ]))

    def test_winner_vertical(self):
        self.assertTrue(is_winner(color = 2, x = 0, y = 1, board = [
            [0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 1, 1, 1, 0],
        ]))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
