#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Subtract one array from another, including all occurrences of each item.
"""

from typing import Iterator, List
import unittest


def diff_array_naive(x: List, y: List) -> List:
    result = []

    for x_elem in x:
        was_found = False

        for y_elem in y:
            if x_elem == y_elem:
                was_found = True
                break

        if not was_found:
            result.append(x_elem)

    return result


def diff_array_iter(x: List, y: List) -> Iterator:
    elem_to_found = dict()

    for x_elem in x:
        was_found = elem_to_found.get(x_elem)

        if was_found is None:
            was_found = elem_to_found[x_elem] = x_elem in y

        if not was_found:
            yield x_elem


class Test (unittest.TestCase):
    diff_array_iter_list = lambda x, y: list(diff_array_iter(x, y))

    diff_array_impls = {
        diff_array_naive,
        diff_array_iter_list,
    }

    def test_empty_arrays(self):
        for diff_array in self.diff_array_impls:
            with self.subTest(diff_array):
                self.assertEqual(diff_array([], []), [])

    def test_empty_left_array(self):
        for diff_array in self.diff_array_impls:
            with self.subTest(diff_array):
                self.assertEqual(diff_array([], [1, 2, 3]), [])

    def test_empty_right_array(self):
        for diff_array in self.diff_array_impls:
            with self.subTest(diff_array):
                self.assertEqual(
                    diff_array([1, 2, 3], []),
                    [1, 2, 3])

    def test_no_common_elements(self):
        for diff_array in self.diff_array_impls:
            with self.subTest(diff_array):
                self.assertEqual(
                    diff_array([1, 2, 3], [4, 5, 6]),
                    [1, 2, 3])

    def test_all_common_elements(self):
        for diff_array in self.diff_array_impls:
            with self.subTest(diff_array):
                self.assertEqual(diff_array([3, 2, 1], [1, 2, 3]), [])

    def test_all_repeat_elements(self):
        for diff_array in self.diff_array_impls:
            with self.subTest(diff_array):
                self.assertEqual(diff_array([1, 1, 1], [1]), [])

    def test_mix_elements(self):
        for diff_array in self.diff_array_impls:
            with self.subTest(diff_array):
                self.assertEqual(
                    diff_array([0, 1, 2, 1, 3, 1, 3], [1, 2]),
                    [0, 3, 3])


if __name__ == '__main__':
    unittest.main(verbosity = 2)