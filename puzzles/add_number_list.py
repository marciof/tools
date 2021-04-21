#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Add two numbers, represented by a linked list with each digit in reverse order,
and return the result also in the same format.
"""

from dataclasses import dataclass
from typing import Optional
import unittest


@dataclass
class Numeral:
    value: Optional[int]
    next: Optional['Numeral'] = None


def as_list(num: int) -> Numeral:
    if num == 0:
        return Numeral(value = 0)

    result_head = Numeral(value = None)
    result_digit = result_head

    while num > 0:
        rem_num = int(num / 10)
        value = num - (rem_num * 10)
        num = rem_num

        next_digit = Numeral(value = value)
        result_digit.next = next_digit
        result_digit = next_digit

    return result_head.next


def as_number(num: Numeral) -> int:
    digit = num
    result = 0
    magnitude = 1

    while digit is not None:
        result += digit.value * magnitude
        magnitude *= 10
        digit = digit.next

    return result


def add(num_1: Numeral, num_2: Numeral) -> Numeral:
    """
    Time: O(max(n, m)), where n=length of number 1, m=length of number 2
    Space: O(max(n, m)), where n=length of number 1, m=length of number 2
    """

    no_op = Numeral(value = 0)
    no_op.next = no_op

    carry = 0
    digit_1 = num_1
    digit_2 = num_2

    result_head = Numeral(value = None)
    result_digit = result_head

    while (carry > 0) or (digit_1 is not no_op) or (digit_2 is not no_op):
        value = digit_1.value + digit_2.value + carry

        if value >= 10:
            carry = 1
            value -= 10
        else:
            carry = 0

        next_digit = Numeral(value = value)
        result_digit.next = next_digit
        result_digit = next_digit

        digit_1 = digit_1.next
        digit_2 = digit_2.next

        if digit_1 is None:
            digit_1 = no_op
        if digit_2 is None:
            digit_2 = no_op

    return result_head.next


class Test (unittest.TestCase):
    def test_add_zeroes(self):
        self.assertEqual(
            as_number(add(as_list(0), as_list(0))),
            0)
    
    def test_add_with_carry(self):
        self.assertEqual(
            as_number(add(as_list(999), as_list(99))),
            1098)

    def test_add_to_zero(self):
        self.assertEqual(
            as_number(add(as_list(12345), as_list(0))),
            12345)
        self.assertEqual(
            as_number(add(as_list(0), as_list(12345))),
            12345)

    def test_add_without_carry(self):
        self.assertEqual(
            as_number(add(as_list(123), as_list(456))),
            579)

    def test_add_different_magnitude(self):
        self.assertEqual(
            as_number(add(as_list(123456), as_list(123))),
            123579)

    def test_add_to_thousands(self):
        self.assertEqual(
            as_number(add(as_list(12345), as_list(10000))),
            22345)


if __name__ == '__main__':
    unittest.main(verbosity = 2)
