#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import unittest

def fizz_buzz(n):
    """
    Count incrementally from 1 to `n`, replacing any number divisible by three
    with the word "Fizz", any number divisible by five with the word "Buzz",
    and for both the word "FizzBuzz".

    Time: O(n)
    """

    for i in range(1, n + 1):
        is_mul_3 = (i % 3) == 0
        is_mul_5 = (i % 5) == 0

        if is_mul_3 and is_mul_5:
            yield 'FizzBuzz'
        elif is_mul_3:
            yield 'Fizz'
        elif is_mul_5:
            yield 'Buzz'
        else:
            yield i

def solve_from_input(file_in):
    n = int(file_in.readline())

    for result in fizz_buzz(n):
        print(result)

class Test (unittest.TestCase):
    def test_until_1(self):
        self.assertListEqual(list(fizz_buzz(1)), [1])

    def test_until_15(self):
        self.assertListEqual(list(fizz_buzz(15)), [
            1,
            2,
            'Fizz',
            4,
            'Buzz',
            'Fizz',
            7,
            8,
            'Fizz',
            'Buzz',
            11,
            'Fizz',
            13,
            14,
            'FizzBuzz',
        ])

if __name__ == '__main__':
    if sys.stdin.isatty():
        unittest.main(verbosity = 2)
    else:
        solve_from_input(sys.stdin)
