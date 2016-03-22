#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

def reverse_span(string, start, end):
    while start < end:
        element = string[start]
        string[start] = string[end]
        string[end] = element

        start += 1
        end -= 1

def reverse(string):
    """
    Reverse word order in a `string` (array) in place.
    """

    reverse_span(string, 0, len(string) - 1)
    last = None

    for i, char in enumerate(string):
        if char != ' ':
            if last is None:
                last = i
        elif last is not None:
            reverse_span(string, last, i - 1)
            last = None

    if last is not None:
        reverse_span(string, last, len(string) - 1)

    return string

class Test (unittest.TestCase):
    def test_empty_string(self):
        array = list('')
        reverse(array)
        self.assertListEqual(array, [])

    def test_single_char(self):
        array = list('a')
        reverse(array)
        self.assertListEqual(array, ['a'])

    def test_no_white_space(self):
        array = list('hello')
        reverse(array)
        self.assertListEqual(array, ['h', 'e', 'l', 'l', 'o'])

    def test_only_white_space(self):
        array = list('     ')
        reverse(array)
        self.assertListEqual(array, [' ', ' ', ' ', ' ', ' '])

    def test_white_space_prefix(self):
        array = list('  abc')
        reverse(array)
        self.assertListEqual(array, ['a', 'b', 'c', ' ', ' '])

    def test_white_space_suffix(self):
        array = list('abc  ')
        reverse(array)
        self.assertListEqual(array, [' ', ' ', 'a', 'b', 'c'])

    def test_multiple_words(self):
        array = list('ab 12  ()   ')
        reverse(array)
        self.assertListEqual(array,
            [' ', ' ', ' ', '(', ')', ' ', ' ', '1', '2', ' ', 'a', 'b'])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
