#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two strings have an identical character set.
Assumes case-insensitivity, and unknown total character size.
"""

import unittest


def has_same_char_set_by_set_cmp_full(str_1: str, str_2: str) -> bool:
    """
    Let:

    - ``k=len(str_1)``, ``m=len(char_set_str_1)``
    - ``l=len(str_2)``, ``n=len(char_set_str_2)``

    Then:

    - ``m<=k``
    - ``n<=l``

    Assuming:

    - ``O(1)`` set lookups

    Then:

    - Time: ``O(k+l)`` -- worst-case identical character sets
    - Space: ``O(k+l)``
    """

    return set(str_1) == set(str_2)


def has_same_char_set_by_set_xor(str_1: str, str_2: str) -> bool:
    """
    Let:

    - ``k=len(str_1)``, ``m=len(char_set_str_1)``
    - ``l=len(str_2)``, ``n=len(char_set_str_2)``

    Then:

    - ``m<=k``
    - ``n<=l``

    Assuming:

    - ``O(1)`` set lookups

    Then:

    - Time: ``O(k+l)``
    - Space: ``O(k+l)`` -- worst-case non-identical character sets
    """

    return (set(str_1) ^ set(str_2)) == set()


def has_same_char_set_by_set_cmp_partial(str_1: str, str_2: str) -> bool:
    """
    Let:

    - ``k=len(str_1)``, ``m=len(char_set_str_1)``
    - ``l=len(str_2)``, ``n=len(char_set_str_2)``

    Then:

    - ``m<=k``
    - ``n<=l``

    Assuming:

    - ``O(1)`` set lookups, removals, insertions

    Then:

    - Time: ``O(k+l)`` -- worst-case identical character sets
    - Space: ``O(k)``
    """

    char_set_1 = set(str_1)
    char_set_2 = set()

    for char_2 in str_2:
        if char_2 in char_set_2:
            continue
        if char_2 not in char_set_1:
            return False

        char_set_1.remove(char_2)
        char_set_2.add(char_2)

    return len(char_set_1) == 0


class BaseTestCase (unittest.TestCase):
    impl = None
    has_same_char_set = property(lambda self: self.impl)

    @classmethod
    def setUpClass(cls):
        if cls.impl is None:
            raise unittest.SkipTest(cls.__name__)

    def test_empty(self):
        self.assertTrue(self.has_same_char_set('', ''))

    def test_superset(self):
        self.assertFalse(self.has_same_char_set('aabc', 'bcb'))

    def test_subset(self):
        self.assertFalse(self.has_same_char_set('bcb', 'aabc'))

    def test_same(self):
        self.assertTrue(self.has_same_char_set('baacab', 'abc'))

    def test_identical(self):
        self.assertTrue(self.has_same_char_set('abc', 'abc'))

    def test_different(self):
        self.assertFalse(self.has_same_char_set('abc', 'def'))

    def test_mix(self):
        self.assertFalse(self.has_same_char_set('abaacab', 'ddcbd'))


class TestCaseSetCmpFull (BaseTestCase):
    impl = staticmethod(has_same_char_set_by_set_cmp_full)

class TestCaseSetXor (BaseTestCase):
    impl = staticmethod(has_same_char_set_by_set_xor)

class TestCaseSetCmpPartial (BaseTestCase):
    impl = staticmethod(has_same_char_set_by_set_cmp_partial)


if __name__ == '__main__':
    unittest.main(verbosity=2)
