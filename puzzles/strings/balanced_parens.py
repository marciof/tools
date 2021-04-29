#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if a string contains only balanced parenthesis.
"""

import unittest


def is_balanced(string: str) -> bool:
    """
    Time: O(n), where n=string length
    Space: O(1)
    """

    depth = 0

    for paren in string:
        if paren == '(':
            depth += 1
        elif paren == ')':
            depth -= 1
            if depth < 0:
                return False
        else:
            raise Exception('Invalid string')

    return depth == 0


class Test (unittest.TestCase):
    def test_balanced(self):
        cases = [
            '',
            '()',
            '(())(())',
            '()()()',
            '(()())',
            '((()))',
        ]

        for case in cases:
            self.assertTrue(is_balanced(case),
                            'Balanced parenthesis: %s' % case)

    def test_unbalanced(self):
        cases = [
            '(',
            ')',
            '(()',
            ')()',
            '())',
            '()(',
        ]

        for case in cases:
            self.assertFalse(is_balanced(case),
                             'Non-balanced parenthesis: %s' % case)


if __name__ == '__main__':
    unittest.main(verbosity=2)
