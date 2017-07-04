#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Check if a student is in trouble based on his/her attendance record:
- o = ok
- l = late
- a = absent

The student is in trouble if 2x absent or 3x late in a row.

Also generate a string up to length N of all combinations where the user
is not in trouble.
"""

import unittest

OK = 'o'
LATE = 'l'
ABSENT = 'a'

def is_in_trouble(attendance):
    """
    Time: O(n)
    Space: O(1)
    """

    num_absent = 0
    num_late = 0

    for record in attendance:
        if record == ABSENT:
            num_absent += 1

            if num_absent == 2:
                return True
        elif record == LATE:
            num_late += 1

            if num_late == 3:
                return True

            continue

        num_late = 0

    return False

def generate_pass(length, num_absent = 0, num_late = 0):
    """
    Time: O(3^n)
    Space: O(n.3^n)
    """

    if length == 0:
        return ['']

    combinations = []

    for c in generate_pass(length - 1, num_absent, 0):
        combinations.append(OK + c)

    if num_absent == 0:
        for c in generate_pass(length - 1, num_absent + 1, 0):
            combinations.append(ABSENT + c)

    if num_late <= 1:
        for c in generate_pass(length - 1, num_absent, num_late + 1):
            combinations.append(LATE + c)

    return combinations

class TestCheckAttendance (unittest.TestCase):
    def test_pass(self):
        self.assertFalse(is_in_trouble(
            OK + LATE + LATE + OK + LATE + ABSENT + OK + OK))

    def test_fail_absent(self):
        self.assertTrue(is_in_trouble(
            OK + ABSENT + OK + OK + OK + ABSENT))

    def test_fail_late(self):
        self.assertTrue(is_in_trouble(
            OK + LATE + OK + OK + ABSENT + LATE + LATE + LATE + OK))

class TestGeneratePass (unittest.TestCase):
    def test_length_3(self):
        self.assertCountEqual(generate_pass(3), {
            'ooo',
            'ooa',
            'ool',
            'oao',
            'oal',
            'olo',
            'ola',
            'oll',
            'aoo',
            'aol',
            'alo',
            'all',
            'loo',
            'loa',
            'lol',
            'lao',
            'lal',
            'llo',
            'lla',
        })

if __name__ == '__main__':
    unittest.main(verbosity = 2)
