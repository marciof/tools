#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Given a hike starting at sea-level count the number of valleys, where a valley
is a sequence of consecutive steps below sea-level, and a mountain is above
sea-level.
"""

import unittest


UP = 'U'
DOWN = 'D'


def count_valleys(steps: str) -> int:
    """
    Time: O(n)
    Space: O(1)
    """

    num_valleys = 0
    level = 0

    for step in steps:
        prev_level = level

        if step == UP:
            level += 1
        elif step == DOWN:
            level -= 1
        else:
            raise Exception('Path string has unknown step characters')

        if (prev_level == 0) and (level < prev_level):
            num_valleys += 1

    return num_valleys


def hike(*args: str) -> str:
    return ''.join(args)


class Test (unittest.TestCase):
    def test_valley_then_mountain(self):
        self.assertEqual(
            count_valleys(hike(DOWN, DOWN, UP, UP, UP, UP, DOWN, DOWN)),
            1)

    def test_valley_with_bump(self):
        self.assertEqual(
            count_valleys(hike(UP, DOWN, DOWN, DOWN, UP, DOWN, UP, UP)),
            1)

    def test_valleys(self):
        path = hike(DOWN, DOWN, UP, UP, DOWN, DOWN, UP, DOWN, UP, UP, UP, DOWN)
        self.assertEqual(count_valleys(path), 2)

    def test_no_hike(self):
        self.assertEqual(count_valleys(hike()), 0)


if __name__ == '__main__':
    unittest.main(verbosity = 2)
