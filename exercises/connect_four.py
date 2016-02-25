#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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

MAX_NR_PIECES = 4


def is_winner(color, x, y, board):
    """
    Checks if the last used piece of `color` at position `x` and `y` in the
    `board` has won the game or not.
    """

    directions = [
        (UP, DOWN),
        (LEFT, RIGHT),
        (UP_LEFT, DOWN_RIGHT),
        (UP_RIGHT, DOWN_LEFT),
    ]

    current_directions = 0

    while current_directions < len(directions):
        (first_dir, second_dir) = directions[current_directions]

        current_directions += 1
        nr_pieces = 1

        for direction in (first_dir, second_dir):
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

                if nr_pieces >= MAX_NR_PIECES:
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
