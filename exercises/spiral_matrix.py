#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Standard:
from __future__ import absolute_import, division, unicode_literals
import collections


Direction = collections.namedtuple('Direction', ['x', 'y'])

UP = Direction(x = 0, y = -1)
DOWN = Direction(x = 0, y = +1)
LEFT = Direction(x = -1, y = 0)
RIGHT = Direction(x = +1, y = 0)


def create_spiral(size):
    if size == 0:
        return []

    directions = [UP, RIGHT, DOWN, LEFT]
    matrix = [[0] * size for _ in range(size)]
    x = y = int((size - 1) / 2)
    direction = 0
    nr_sides = 0
    side_length = 0
    max_side_length = 1
    n = 1

    while (y >= 0) and (x >= 0) and (y < size) and (x < size):
        matrix[y][x] = n
        n += 1
        side_length += 1

        if side_length == max_side_length:
            nr_sides += 1
            side_length = 0
            direction = (direction + 1) % len(directions)

        if nr_sides == 4:
            nr_sides = 0
            max_side_length += 2
            x += LEFT.x
            y += LEFT.y
        else:
            x += directions[direction].x
            y += directions[direction].y

    return matrix


def print_matrix(matrix):
    for row in matrix:
        print row


if __name__ == '__main__':
    print_matrix(create_spiral(4))
