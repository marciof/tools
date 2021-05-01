#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
List the top most frequent values in an array.
"""

import unittest


# TODO Use a heap.
def list_most_frequent(values, n):
    if n == 0:
        return []

    count = {}

    for value in values:
        if value in count:
            count[value] += 1
        else:
            count[value] = 1

    most_frequent = []

    for value, count in sorted(count.items(), key=lambda item: -item[1]):
        most_frequent.append(value)

        if len(most_frequent) == n:
            break

    return most_frequent


class Test (unittest.TestCase):
    def test_top_zero(self):
        self.assertEqual(
            list_most_frequent(['a', 'b', 'c'], 0),
            [])

    def test_empty(self):
        self.assertEqual(
            list_most_frequent([], 10),
            [])

    def test_mix(self):
        self.assertEqual(
            list_most_frequent(['a', 'b', 'b', 'c', 'a', 'b', 'd'], 2),
            ['b', 'a'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
