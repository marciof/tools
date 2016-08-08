#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Evaluate a Polish notation expression, that uses only single digit integers
and the four main arithmetic binary operators. Assume input is valid.
"""

import operator
import unittest

OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
}

def _calc_iter(expr):
    token = next(expr)

    if token in OPERATORS:
        left = _calc_iter(expr)
        right = _calc_iter(expr)
        return OPERATORS[token](left, right)
    else:
        return int(token)

def calc_functional(expr):
    return _calc_iter(iter(expr))

def calc_loop(expr):
    result = []

    for token in reversed(expr):
        if token in OPERATORS:
            left = result.pop()
            right = result.pop()
            result.append(OPERATORS[token](left, right))
        else:
            result.append(int(token))

    return result.pop()

class TestSuite:
    def test_single_operand(self):
        self.assertEqual(self.calc('3'), 3)

    def test_single_operator(self):
        self.assertEqual(self.calc('-28'), -6)

    def test_mix(self):
        self.assertEqual(self.calc('-*/5-7+113+2+11'), -1)

class TestFunctional (unittest.TestCase, TestSuite):
    def calc(self, expr):
        return calc_functional(expr)

class TestLoop (unittest.TestCase, TestSuite):
    def calc(self, expr):
        return calc_loop(expr)

if __name__ == '__main__':
    unittest.main(verbosity = 2)
