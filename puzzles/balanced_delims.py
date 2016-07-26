#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if a `string` contains only balanced delimiters.

Time: O(n)
"""

import unittest
import sys

def is_balanced(string):
    expected = []

    open_to_close = {
        '(': ')',
        '[': ']',
        '{': '}',
    }

    for char in string:
        if char in open_to_close:
            expected.append(open_to_close[char])
        elif (len(expected) > 0) and (expected[-1] == char):
            expected.pop()
        else:
            return False

    return len(expected) == 0

class Test (unittest.TestCase):
    def test_balanced(self):
        cases = [
            '([])([])',
            '()[]{}',
            '([]{})',
            '([{}])',
        ]

        for case in cases:
            self.assertTrue(is_balanced(case))

    def test_unbalanced(self):
        cases = [
            '([)]',
            '([]',
            '[])',
            '([})',
        ]

        for case in cases:
            self.assertFalse(is_balanced(case))

if __name__ == '__main__':
    if sys.stdin.isatty():
        unittest.main(verbosity = 2)
    else:
        for line in sys.stdin:
            if line[0] in '(){}[]':
                if is_balanced(line.strip()):
                    print('YES')
                else:
                    print('NO')
