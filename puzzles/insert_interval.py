#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Merge an `interval` into a list of sorted disjoint `intervals`.
"""

import unittest

LO = 0
HI = 1

def insert(intervals, interval):
    merged = []
    intervals_it = iter(intervals)

    for iv in intervals_it:
        if interval[LO] > iv[HI]:
            merged.append(iv)
        elif interval[HI] < iv[LO]:
            merged.append(interval)
            merged.append(iv)
            merged.extend(intervals_it)
            break
        else:
            interval = [min(iv[LO], interval[LO]), max(iv[HI], interval[HI])]
    else:
        merged.append(interval)

    return merged

class Test (unittest.TestCase):
    def test_no_intervals(self):
        self.assertEqual(
            insert([], [2, 5]),
            [[2, 5]])

    def test_inside_interval(self):
        self.assertEqual(
            insert([[1, 5], [10, 15], [20, 25]], [10, 12]),
            [[1, 5], [10, 15], [20, 25]])

    def test_outside_interval(self):
        self.assertEqual(
            insert([[1, 5], [10, 15], [20, 25]], [17, 19]),
            [[1, 5], [10, 15], [17, 19], [20, 25]])

    def test_intersect_interval(self):
        self.assertEqual(
            insert([[1, 5], [10, 15], [20, 25]], [15, 17]),
            [[1, 5], [10, 17], [20, 25]])

    def test_intersect_intervals(self):
        self.assertEqual(
            insert([[1, 5], [10, 15], [20, 25]], [15, 27]),
            [[1, 5], [10, 27]])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
