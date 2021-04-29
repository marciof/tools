#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if a string contains only balanced delimiters (eg. (), [], {}).
"""

import unittest
import sys


def is_balanced(string: str) -> bool:
    """
    Time: O(n), where n=string length
    Space: O(n), worst-case it consists of open delimiters only
    """

    open_to_close = {
        '(': ')',
        '[': ']',
        '{': '}',
    }

    expected_close = []

    for char in string:
        if char in open_to_close:
            expected_close.append(open_to_close[char])
        elif (len(expected_close) > 0) and (expected_close[-1] == char):
            expected_close.pop()
        else:
            return False

    return len(expected_close) == 0


class Test (unittest.TestCase):
    def test_balanced(self):
        cases = [
            '([])([])',
            '()[]{}',
            '([]{})',
            '([{}])',
            '(()[{}])',
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
        unittest.main(verbosity=2)
    else:
        for line in sys.stdin:
            if line[0] in '(){}[]':
                if is_balanced(line.strip()):
                    print('YES')
                else:
                    print('NO')
