#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Generate all possible ways to interleave strings `str_a` and `str_b`.

For example, if the two strings are 'ab' and 'cd', the output is:
['abcd', 'acbd', 'acdb', 'cabd', 'cadb', 'cdab']
As you can see, 'a' is always before 'b', and 'c' is always before 'd'.

Time: O(n+m), where n = len(str_a), m = len(str_b)
"""

import unittest

def interleave(str_a, str_b):
    if str_a == '':
        return [str_b]

    if str_b == '':
        return [str_a]

    combinations = []

    for c in interleave(str_a[1:], str_b):
        combinations.append(str_a[0] + c)

    for c in interleave(str_a, str_b[1:]):
        combinations.append(str_b[0] + c)

    return combinations

class Test (unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(interleave('', ''), [''])
        self.assertEqual(interleave('xyz', ''), ['xyz'])
        self.assertEqual(interleave('', 'abc'), ['abc'])

    def test_char(self):
        self.assertCountEqual(
            interleave('a', 'b'),
            ['ab', 'ba'])

    def test_string(self):
        self.assertCountEqual(
            interleave('ab', 'cd'),
            ['abcd', 'acbd', 'acdb', 'cabd', 'cadb', 'cdab'])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
