#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

class Node:
    def __init__(self, value, next = None):
        self.value = value
        self.next = next

    def __str__(self):
        return '<%r at %x>' % (self.value, id(self))

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

    def step(node):
        return None if node is None else node.next

    slow = l
    fast = l

    while True:
        slow = step(slow)
        fast = step(step(fast))

        if fast is None:
            return (False, None)

        if slow == fast:
            break

    slow = l

    while slow != fast:
        slow = step(slow)
        fast = step(fast)

    return (True, slow)

class Test (unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(has_cycle(make_list()), (False, None))

    def test_single_node(self):
        self.assertEqual(has_cycle(make_list('a')), (False, None))

    def test_multiple_nodes(self):
        self.assertEqual(has_cycle(make_list('a', 'b', 'c')), (False, None))

    def test_multiple_repeated_nodes(self):
        self.assertEqual(has_cycle(make_list('a', 'a', 'a')), (False, None))

    def test_cycle_with_single_node(self):
        l = make_list('x')
        l.next = l
        self.assertEqual(has_cycle(l), (True, l))

    def test_cycle_with_multiple_nodes(self):
        l = make_list('a', 'b', 'c')
        c = l.next.next

        c.next = l
        self.assertEqual(has_cycle(l), (True, l))

        c.next = l.next
        self.assertEqual(has_cycle(l), (True, l.next))

        c.next = l.next.next
        self.assertEqual(has_cycle(l), (True, l.next.next))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
