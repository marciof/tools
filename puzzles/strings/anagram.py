#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two words are an anagram of each other.
Assumes case-insensitivity.

Wikipedia: "An anagram is a word or phrase formed by rearranging the
letters of a different word or phrase, typically using all the original
letters exactly once."
"""

from typing import Dict
import unittest


def is_anagram_by_sorting(word_1: str, word_2: str) -> bool:
    """
    """

    if len(word_1) != len(word_2):
        return False
    else:
        return sorted(word_1) == sorted(word_2)


def is_anagram_by_splicing(word_1: str, word_2: str) -> bool:
    """
    """

    if len(word_1) != len(word_2):
        return False
    if len(word_1) == 0 and len(word_2) == 0:
        return True

    i = word_2.find(word_1[0])

    if i < 0:
        return False

    return is_anagram_by_splicing(word_1[1:], word_2[:i] + word_2[i+1:])


def is_anagram_by_histogram(word_1: str, word_2: str) -> bool:
    """
    """

    if len(word_1) != len(word_2):
        return False

    hist_1: Dict[str, int] = {}

    for char_1 in word_1:
        hist_1[char_1] = hist_1.get(char_1, 0) + 1

    for char_2 in word_2:
        if char_2 not in hist_1:
            return False

        hist_1[char_2] -= 1

        if hist_1[char_2] == 0:
            del hist_1[char_2]

    return len(hist_1) == 0


class BaseTestCase (unittest.TestCase):
    impl = None
    is_anagram = property(lambda self: self.impl)

    @classmethod
    def setUpClass(cls):
        if cls.impl is None:
            raise unittest.SkipTest(cls.__name__)

    def test_empty(self):
        self.assertTrue(self.is_anagram('', ''))

    def test_identical_words(self):
        self.assertTrue(self.is_anagram('cat', 'cat'))

    def test_match_no_dup_letters(self):
        self.assertTrue(self.is_anagram('cat', 'act'))

    def test_match_dup_letters(self):
        self.assertTrue(self.is_anagram('state', 'taste'))

    def test_superset(self):
        self.assertFalse(self.is_anagram('cart', 'cat'))

    def test_subset(self):
        self.assertFalse(self.is_anagram('cat', 'cart'))


class TestCaseBySorting (BaseTestCase):
    impl = staticmethod(is_anagram_by_sorting)

class TestCaseBySplicing (BaseTestCase):
    impl = staticmethod(is_anagram_by_splicing)

class TestCaseByHistogram (BaseTestCase):
    impl = staticmethod(is_anagram_by_histogram)


if __name__ == '__main__':
    unittest.main(verbosity=2)
