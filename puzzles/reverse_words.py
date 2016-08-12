#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Reverse each word in a `string` (array) in place.

Reverse word order in a `string` (array) in place.
"""

import unittest

def reverse_span(string, begin, end):
    while begin < end:
        (string[begin], string[end]) = (string[end], string[begin])
        begin += 1
        end -= 1

def reverse_words(string):
    begin = None

    for i, char in enumerate(string):
        if char != ' ':
            if begin is None:
                begin = i
        elif begin is not None:
            reverse_span(string, begin, i - 1)
            begin = None

    if begin is not None:
        reverse_span(string, begin, len(string) - 1)

def reverse_word_order(string):
    reverse_span(string, 0, len(string) - 1)
    reverse_words(string)

class TestReverseWords (unittest.TestCase):
    def test_empty_string(self):
        array = list('')
        reverse_words(array)
        self.assertListEqual(array, [])

    def test_single_char(self):
        array = list('a')
        reverse_words(array)
        self.assertListEqual(array, ['a'])

    def test_no_white_space(self):
        array = list('hello')
        reverse_words(array)
        self.assertListEqual(array, ['o', 'l', 'l', 'e', 'h'])

    def test_only_white_space(self):
        array = list('     ')
        reverse_words(array)
        self.assertListEqual(array, [' ', ' ', ' ', ' ', ' '])

    def test_white_space_prefix(self):
        array = list('  abc')
        reverse_words(array)
        self.assertListEqual(array, [' ', ' ', 'c', 'b', 'a'])

    def test_white_space_suffix(self):
        array = list('abc  ')
        reverse_words(array)
        self.assertListEqual(array, ['c', 'b', 'a', ' ', ' '])

    def test_multiple_words(self):
        array = list('ab 12  ()   ')
        reverse_words(array)
        self.assertListEqual(array,
            ['b', 'a', ' ', '2', '1', ' ', ' ', ')', '(', ' ', ' ', ' '])

class TestReverseWordOrder (unittest.TestCase):
    def test_empty_string(self):
        array = list('')
        reverse_word_order(array)
        self.assertListEqual(array, [])

    def test_single_char(self):
        array = list('a')
        reverse_word_order(array)
        self.assertListEqual(array, ['a'])

    def test_no_white_space(self):
        array = list('hello')
        reverse_word_order(array)
        self.assertListEqual(array, ['h', 'e', 'l', 'l', 'o'])

    def test_only_white_space(self):
        array = list('     ')
        reverse_word_order(array)
        self.assertListEqual(array, [' ', ' ', ' ', ' ', ' '])

    def test_white_space_prefix(self):
        array = list('  abc')
        reverse_word_order(array)
        self.assertListEqual(array, ['a', 'b', 'c', ' ', ' '])

    def test_white_space_suffix(self):
        array = list('abc  ')
        reverse_word_order(array)
        self.assertListEqual(array, [' ', ' ', 'a', 'b', 'c'])

    def test_multiple_words(self):
        array = list('ab 12  ()   ')
        reverse_word_order(array)
        self.assertListEqual(array,
            [' ', ' ', ' ', '(', ')', ' ', ' ', '1', '2', ' ', 'a', 'b'])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
