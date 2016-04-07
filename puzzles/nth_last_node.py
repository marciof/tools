#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import io
import re
import sys
import unittest

VALUE = 0
NEXT = 1

def nth_last_node(lst, n):
    last_node = lst
    curr_node = lst
    pos = 0

    while pos < n:
        if curr_node is None:
            return None

        pos += 1
        curr_node = curr_node[NEXT]

    while curr_node is not None:
        last_node = last_node[NEXT]
        curr_node = curr_node[NEXT]

    return last_node

def solve_from_input(file_in):
    m = int(file_in.readline())
    head = [None, None]
    last_node = head
    last_value = ''

    while True:
        buffer = file_in.read(io.DEFAULT_BUFFER_SIZE)

        if not buffer:
            break

        values = re.split(r'\b \b', last_value + buffer)
        last_value = values.pop()

        for value in values:
            node = [int(value), None]
            last_node[NEXT] = node
            last_node = node

    if last_value:
        node = [int(last_value), None]
        last_node[NEXT] = node

    nth_node = nth_last_node(head[NEXT], m)

    if nth_node is None:
        print('NIL')
    else:
        print(nth_node[VALUE])

def make_list(*values):
    if len(values) == 0:
        return None
    else:
        return [values[0], make_list(*values[1:])]

class Test (unittest.TestCase):
    def test_empty_list(self):
        self.assertIsNone(nth_last_node(make_list(), 1))

    def test_single_element(self):
        l = make_list('x')
        self.assertIsNone(nth_last_node(l, 2))
        self.assertEqual(nth_last_node(l, 1)[VALUE], 'x')

    def test_multiple_elements(self):
        l = make_list('x', 'y', 'z')
        self.assertIsNone(nth_last_node(l, 4))
        self.assertEqual(nth_last_node(l, 3)[VALUE], 'x')
        self.assertEqual(nth_last_node(l, 2)[VALUE], 'y')
        self.assertEqual(nth_last_node(l, 1)[VALUE], 'z')

if __name__ == '__main__':
    if sys.stdin.isatty():
        unittest.main(verbosity = 2)
    else:
        solve_from_input(sys.stdin)
