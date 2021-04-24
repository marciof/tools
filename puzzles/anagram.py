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


def is_anagram(word1: str, word2: str) -> bool:
    """
    Time: O(k+l), where k=length of word_1, l=length of word_2
    Space: O(l), worst-case every character is unique in word_2
    """

    if len(word1) != len(word2):
        return False

    word2_letters = set(word2)

    for word1_letter in word1:
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


class Test (unittest.TestCase):
    is_anagram_impls = {
        is_anagram,
        is_anagram_manual,
    }

    def test_empty(self):
        for is_anagram_impl in self.is_anagram_impls:
            with self.subTest(is_anagram_impl):
                self.assertTrue(is_anagram_impl('', ''))

    def test_match(self):
        for is_anagram_impl in self.is_anagram_impls:
            with self.subTest(is_anagram_impl):
                self.assertTrue(is_anagram_impl('cat', 'act'))

    def test_same(self):
        for is_anagram_impl in self.is_anagram_impls:
            with self.subTest(is_anagram_impl):
                self.assertTrue(is_anagram_impl('cat', 'cat'))

    def test_count_mismatch(self):
        for is_anagram_impl in self.is_anagram_impls:
            with self.subTest(is_anagram_impl):
                self.assertFalse(is_anagram_impl('cart', 'cataract'))

    def test_superset(self):
        for is_anagram_impl in self.is_anagram_impls:
            with self.subTest(is_anagram_impl):
                self.assertFalse(is_anagram_impl('cart', 'cat'))

    def test_subset(self):
        for is_anagram_impl in self.is_anagram_impls:
            with self.subTest(is_anagram_impl):
                self.assertFalse(is_anagram_impl('cat', 'cart'))


if __name__ == '__main__':
    unittest.main(verbosity = 2)
