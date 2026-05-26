#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two strings have an identical character set.
Assumes case-insensitivity, and unknown total character size.
"""

import unittest


def has_same_char_set_by_set_cmp(str_1: str, str_2: str) -> bool:
    """
    Where: k=len(str_1), l=len(str_2)

    - Time: O(k+l) -- loops over both strings
    - Space: O(k+l) -- worst-case all unique characters
    """

    return set(str_1) == set(str_2)


def has_same_char_set_by_set_xor(str_1: str, str_2: str) -> bool:
    """
    Where:

    - Time:
    - Space:
    """

    return len(set(str_1) ^ set(str_2)) == 0


def has_same_char_set_by_set_cmp_fail_fast(str_1: str, str_2: str) -> bool:
    """
    Where: k=len(str_1), l=len(str_2), n=len(char_set_1)

    - Time: O(k+l) -- worst-case all identical characters
    - Space: O(k) or O(n) -- worst-case all unique characters
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


class TestCaseSetCmp (BaseTestCase):
    impl = staticmethod(has_same_char_set_by_set_cmp)

class TestCaseSetXor (BaseTestCase):
    impl = staticmethod(has_same_char_set_by_set_xor)

class TestCaseSetCmpFailFast (BaseTestCase):
    impl = staticmethod(has_same_char_set_by_set_cmp_fail_fast)


if __name__ == '__main__':
    unittest.main(verbosity=2)
