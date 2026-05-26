#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if two words are an anagram of each other.

From Wikipedia: "An anagram is a word or phrase formed by rearranging the
letters of a different word or phrase, typically using all the original
letters exactly once."
"""

from typing import Dict
import unittest


def is_anagram_v0(word_1: str, word_2: str) -> bool:
    """
    Time: O(k+l), where k=length of word_1, l=length of word_2
    Space: O(l), worst-case every character is unique in word_2
    """

    if len(word_1) != len(word_2):
        return False

    word2_letters = set(word_2)

    for word1_letter in word_1:
        if word1_letter not in word2_letters:
            return False
        word2_letters.remove(word1_letter)

    return len(word2_letters) == 0


def is_anagram_manual(word_1: str, word_2: str) -> bool:
    """
    Time: O(k+l), where k=length of word_1, l=length of word_2
    Space: O(k), worst-case every character is unique in word_1
    """

    # Optimization: if of different lengths, return false.

    char_count_1: Dict[str, int] = {}

    for char in word_1:
        char_count_1[char] = char_count_1.get(char, 0) + 1

    for char in word_2:
        if char not in char_count_1:
            return False

        char_count_1[char] -= 1

        if char_count_1[char] == 0:
            del char_count_1[char]

    return len(char_count_1) == 0


class BaseTestCase (unittest.TestCase):
    impl = None
    is_anagram = property(lambda self: self.impl)

    @classmethod
    def setUpClass(cls):
        if cls.impl is None:
            raise unittest.SkipTest(cls.__name__)

    def test_empty(self):
        self.assertTrue(self.is_anagram('', ''))

    def test_match(self):
        self.assertTrue(self.is_anagram('cat', 'act'))

    def test_same(self):
        self.assertTrue(self.is_anagram('cat', 'cat'))

    def test_count_mismatch(self):
        self.assertFalse(self.is_anagram('cart', 'cataract'))

    def test_superset(self):
        self.assertFalse(self.is_anagram('cart', 'cat'))

    def test_subset(self):
        self.assertFalse(self.is_anagram('cat', 'cart'))


class TestCaseV0 (BaseTestCase):
    impl = staticmethod(is_anagram_v0)

class TestCaseManual (BaseTestCase):
    impl = staticmethod(is_anagram_manual)


if __name__ == '__main__':
    unittest.main(verbosity=2)
