#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Generate all possible coin combinations using any from `coins`
that when added equal `amount`.

https://programmingpraxis.com/2013/05/17/coin-change-part-1/2/
http://www.geeksforgeeks.org/dynamic-programming-set-7-coin-change/
https://www.hackerrank.com/contests/programming-interview-questions/challenges/coin-change
"""

from collections import Counter
import unittest

def generate(amount, coins):
    combs = [[] for _ in range(amount + 1)]
    combs[0] = [[]]

    for coin in coins:
        i = coin

        while i <= amount:
            for comb in combs[i - coin]:
                combs[i].append([coin] + comb)

            i += 1

    return combs[amount]

class Test (unittest.TestCase):
    def test_few_combinations(self):
        self.assertCountEqual(

            map(Counter,
                generate(10, [2, 3])),

            map(Counter, [
                [2, 2, 2, 2, 2],
                [2, 2, 3, 3],
            ]))

    def test_some_combinations(self):
        self.assertCountEqual(

            map(Counter,
                generate(4, [3, 1, 2])),

            map(Counter, [
                [1, 1, 1, 1],
                [1, 1, 2],
                [2, 2],
                [1, 3],
            ]))

    def test_many_combinations(self):
        self.assertCountEqual(

            map(Counter,
                generate(10, [2, 5, 3, 6])),

            map(Counter, [
                [2, 2, 2, 2, 2],
                [2, 2, 3, 3],
                [2, 2, 6],
                [2, 3, 5],
                [5, 5],
            ]))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
