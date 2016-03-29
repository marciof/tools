#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import collections
import unittest

Node = collections.namedtuple('Node', ['value', 'next'])

def make_list(*values):
    if len(values) == 0:
        return None

    return Node(
        value = values[0],
        next = make_list(*values[1:]))

def print_list(l):
    while l is not None:
        print(l.value, end ='')

        if l.next:
            print(', ', end = '')
            l = l.next
        else:
            break

    print()

def nth_last_node(l, n):
    """
    Return the `n`-th last node in a singly-linked list `l`.

    Time: O(n)
    Space: O(1)
    """

    last = l
    current = l
    pos = 0

    while pos < n:
        if current is None:
            return None

        pos += 1
        current = current.next

    while current is not None:
        last = last.next
        current = current.next

    return last

class Test (unittest.TestCase):
    def test_empty_list(self):
        self.assertIsNone(nth_last_node(make_list(), 1))

    def test_single_element(self):
        l = make_list('x')
        self.assertIsNone(nth_last_node(l, 2))
        self.assertEqual(nth_last_node(l, 1).value, 'x')

    def test_multiple_elements(self):
        l = make_list('x', 'y', 'z')
        self.assertIsNone(nth_last_node(l, 4))
        self.assertEqual(nth_last_node(l, 3).value, 'x')
        self.assertEqual(nth_last_node(l, 2).value, 'y')
        self.assertEqual(nth_last_node(l, 1).value, 'z')

if __name__ == '__main__':
    unittest.main(verbosity = 2)
