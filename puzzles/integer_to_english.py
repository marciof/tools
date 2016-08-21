#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Convert a non-negative integer (up to millions) to written English.
"""

import unittest

less_twenty_to_word = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
    11: 'eleven',
    12: 'twelve',
    13: 'thirteen',
    14: 'fourteen',
    15: 'fifteen',
    16: 'sixteen',
    17: 'seventeen',
    18: 'eighteen',
    19: 'nineteen',
}

tens_to_word = {
    20: 'twenty',
    30: 'thirty',
    40: 'forty',
    50: 'fifty',
    60: 'sixty',
    70: 'seventy',
    80: 'eighty',
    90: 'ninety',
}

def split_digits(n, mask):
    left = int(n / mask)
    right = n - (left * mask)

    return (left, right)

def to_eng(n):
    if n == 0:
        return 'zero'

    words = []
    (thousands, hundreds) = split_digits(n, 1000)

    if hundreds > 0:
        (hundred, tens) = split_digits(hundreds, 100)

        if hundred > 0:
            words.append(less_twenty_to_word[hundred])
            words.append('hundred')

        if tens in less_twenty_to_word:
            words.append(less_twenty_to_word[tens])
        elif tens > 0:
            (_, digit) = split_digits(tens, 10)
            words.append(tens_to_word[tens - digit])

            if digit > 0:
                words.append(less_twenty_to_word[digit])

    if thousands > 0:
        (millions, thousands) = split_digits(thousands, 1000)
        words[0:0] = [to_eng(thousands), 'thousand']

        if millions > 0:
            words[0:0] = [to_eng(millions), 'million']

    return ' '.join(words)

class Test (unittest.TestCase):
    def test_zero(self):
        self.assertEqual(to_eng(0), 'zero')

    def test_less_ten(self):
        self.assertEqual(to_eng(7), 'seven')

    def test_between_ten_twenty(self):
        self.assertEqual(to_eng(10), 'ten')
        self.assertEqual(to_eng(12), 'twelve')

    def test_between_twenty_hundred(self):
        self.assertEqual(to_eng(30), 'thirty')
        self.assertEqual(to_eng(48), 'forty eight')

    def test_between_hundred_thousand(self):
        self.assertEqual(to_eng(100), 'one hundred')
        self.assertEqual(to_eng(210), 'two hundred ten')
        self.assertEqual(to_eng(417), 'four hundred seventeen')

    def test_between_thousand_million(self):
        self.assertEqual(to_eng(1234), 'one thousand two hundred thirty four')
        self.assertEqual(to_eng(9000), 'nine thousand')

    def test_above_million(self):
        self.assertEqual(to_eng(1234560),
            'one million two hundred thirty four thousand five hundred sixty')

if __name__ == '__main__':
    unittest.main(verbosity = 2)
