#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
List all possible balanced parenthesis combinations up to `total` pairs.
"""

from typing import Iterator, List
import unittest


def permutate_recur(
        max_num_pairs: int,
        parens: str = '()',
        has_nesting: bool = False) -> Iterator[str]:

    if max_num_pairs <= 0:
        return
    elif max_num_pairs == 1:
        yield parens
    else:
        yield from permutate_recur(max_num_pairs - 1, '(' + parens + ')', True)
        yield from permutate_recur(max_num_pairs - 1, '()' + parens, False)
        if has_nesting:
            yield from permutate_recur(max_num_pairs - 1, parens + '()', True)


def permutate(total: int, num_open: int = 0, num_closed: int = 0) -> List[str]:
    """
    Time: O(2^n), two branches of recursive calls for each call
    Space: O(2^n)
    """

    combinations = []

    if num_open < total:
        for c in permutate(total, num_open + 1, num_closed):
            combinations.append('(' + c)

    if num_closed < num_open:
        for c in permutate(total, num_open, num_closed + 1):
            combinations.append(')' + c)
        else:
            if (num_closed + 1) == total:
                combinations.append(')')

    return combinations


class Test (unittest.TestCase):
    """
    Each test case uses `sorted` so that comparison works irrespective of
    the generated order, while at the same time catching errors if duplicate
    elements are generated.
    """

    permutate_impls = {
        permutate_recur,
        permutate,
    }

    def test_count_0(self):
        for permutate_impl in self.permutate_impls:
            with self.subTest(permutate_impl):
                self.assertEqual(list(sorted(permutate_impl(0))), [])

    def test_count_1(self):
        for permutate_impl in self.permutate_impls:
            with self.subTest(permutate_impl):
                self.assertEqual(list(sorted(permutate_impl(1))), ['()'])

    def test_count_2(self):
        for permutate_impl in self.permutate_impls:
            with self.subTest(permutate_impl):
                self.assertEqual(
                    list(sorted(permutate_impl(2))),
                    sorted(['()()', '(())']))

    def test_count_3(self):
        for permutate_impl in self.permutate_impls:
            with self.subTest(permutate_impl):
                self.assertEqual(
                    list(sorted(permutate_impl(3))),
                    sorted([
                        '()()()',
                        '((()))',
                        '(()())',
                        '(())()',
                        '()(())',
                    ]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
