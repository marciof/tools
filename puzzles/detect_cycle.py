#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Floyd's "tortoise and hare" algorithm:

1. Keep two pointers: `slow` steps one node at a time, `fast` steps double.
2. If they ever meet, then there's a cycle.
3. Otherwise, there's no cycle.

To find the start of the cycle:

1. Reset `slow` to the start.
2. Step both `slow` and `fast` now one node at a time.
3. The node where they meet is the start of the cycle.

Why does this work?

Imagine two people racing around a track, one twice as fast as the other. If
they start off at the same place, they will next meet at the start of the next
lap.

After some moves both pointers will be in the cycle. With the next moves you
can be sure that both will meet at some point since with every step the
difference between them reduces by 1.

Hypothesis:

- `m` = distance from first node to start of cycle (# nodes)
- `l` = length of cycle (# nodes)
- `k` = distance of meeting point from start of cycle (# nodes)
- `dist_S = m + p*l + k`
- `dist_F = m + q*l + k` where `q > p` since this one goes faster
- `2 * dist_S = dist_F` (note that any multiple would work)
- `2 * (m + p*l + k) = m + q*l + k`
- `m + 2*p*l + k = q*l`
- `m + k = (q - 2*p)*l` implies `m+k` is an integer multiple of the cycle length
"""

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

    Returns `(has_cycle, cycle start node, previous node)`.
    """

    def step(node):
        return None if node is None else node.next

    slow = l
    fast = l
    previous = None

    while True:
        slow = step(slow)
        previous = step(fast)
        fast = step(previous)

        if fast is None:
            return (False, None, None)

        if slow == fast:
            break

    slow = l

    while slow != fast:
        slow = step(slow)
        previous = fast
        fast = step(fast)

    return (True, slow, previous)

class Test (unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(
            has_cycle(make_list()),
            (False, None, None))

    def test_single_node(self):
        self.assertEqual(
            has_cycle(make_list('a')),
            (False, None, None))

    def test_multiple_nodes(self):
        self.assertEqual(
            has_cycle(make_list('a', 'b', 'c')),
            (False, None, None))

    def test_multiple_repeated_nodes(self):
        self.assertEqual(
            has_cycle(make_list('a', 'a', 'a')),
            (False, None, None))

    def test_cycle_with_single_node(self):
        l = make_list('x')
        l.next = l
        self.assertEqual(has_cycle(l), (True, l, l))

    def test_cycle_with_multiple_nodes(self):
        l = make_list('a', 'b', 'c')
        c = l.next.next

        c.next = l
        self.assertEqual(has_cycle(l), (True, l, c))

        c.next = l.next
        self.assertEqual(has_cycle(l), (True, l.next, c))

        c.next = l.next.next
        self.assertEqual(has_cycle(l), (True, l.next.next, c))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
