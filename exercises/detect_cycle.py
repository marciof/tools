#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

class Node:
    def __init__(self, value, next = None):
        self.value = value
        self.next = next

def make_list(*values):
    first = None
    previous = None

    for value in values:
        node = Node(value)

        if previous is not None:
            previous.next = node

        if first is None:
            first = node

        previous = node

    return first

def print_list(l):
    while True:
        print(l.value, end ='')

        if l.next:
            print(', ', end = '')
            l = l.next
        else:
            break

    print()

def has_cycle(l):
    """
    Detect a cycle in a linked list. (Floyd's "tortoise and hare" algorithm.)
    """

    slow = l
    fast = l

    while slow and fast:
        slow = slow.next
        fast = fast.next

        if fast is None:
            return False

        fast = fast.next

        if slow == fast:
            return True

    return False

class Test (unittest.TestCase):
    def test_empty_list(self):
        self.assertFalse(has_cycle(None))

    def test_single_node(self):
        self.assertFalse(has_cycle(make_list('a')))

    def test_multiple_nodes(self):
        self.assertFalse(has_cycle(make_list('a', 'b', 'c')))

    def test_multiple_repeated_nodes(self):
        self.assertFalse(has_cycle(make_list('a', 'a', 'a')))

    def test_cycle_with_single_node(self):
        l = make_list('a')
        l.next = l
        self.assertTrue(has_cycle(l))

    def test_cycle_with_multiple_nodes(self):
        l = make_list('a', 'b', 'c')
        c = l.next.next

        c.next = l
        self.assertTrue(has_cycle(l))

        c.next = l.next
        self.assertTrue(has_cycle(l))

        c.next = l.next.next
        self.assertTrue(has_cycle(l))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
