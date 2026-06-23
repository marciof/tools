#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
List all possible balanced parenthesis combinations up to `total` pairs.

Example: 2 total pairs gives '()()' and '(())'
"""

from typing import Iterator, List
import unittest


def permute_recur(
        max_num_pairs: int,
        parens: str = '()',
        has_nesting: bool = False) -> Iterator[str]:
    """
    Time: O(2^n), two branches (+/- 1) of recursive calls for each call
    Space: O(2^n)
    """

    if max_num_pairs <= 0:
        return
    elif max_num_pairs == 1:
        yield parens
    else:
        yield from permute_recur(max_num_pairs - 1, '(' + parens + ')', True)
        yield from permute_recur(max_num_pairs - 1, '()' + parens, False)
        if has_nesting:
            yield from permute_recur(max_num_pairs - 1, parens + '()', True)


def permute(total: int, num_open: int = 0, num_closed: int = 0) -> List[str]:
    """
    Time: O(2^n), two branches of recursive calls for each call
    Space: O(2^n)
    """

    combinations = []

    if num_open < total:
        for c in permute(total, num_open + 1, num_closed):
            combinations.append('(' + c)

    if num_closed < num_open:
        for c in permute(total, num_open, num_closed + 1):
            combinations.append(')' + c)
        else:
            if (num_closed + 1) == total:
                combinations.append(')')

    return combinations


class BaseTestCase (unittest.TestCase):
    """
    Each test case sorts the result so that comparison works irrespective of
    the generated order, while at the same time catching errors if duplicate
    elements are given.
    """

    impl = None
    list_pairs = property(lambda self: self.impl)

    @classmethod
    def setUpClass(cls):
        if cls.impl is None:
            raise unittest.SkipTest(cls.__name__)

    def test_0_pairs(self):
        self.assertEqual(self.list_pairs(0), [])

    def test_1_pair(self):
        self.assertEqual(self.list_pairs(1), ['()'])

    def test_2_pairs(self):
        self.assertEqual(
            sorted(self.list_pairs(2)),
            sorted(['()()', '(())']))

    def test_3_pairs(self):
        self.assertEqual(
            sorted(self.list_pairs(3)),
            sorted([
                '()()()',
                '((()))',
                '(()())',
                '(())()',
                '()(())',
            ]))


class TestCaseByPermuteRecur (BaseTestCase):
    impl = staticmethod(permute_recur)

class TestCaseByPermute (BaseTestCase):
    impl = staticmethod(permute)


if __name__ == '__main__':
    unittest.main(verbosity=2)
