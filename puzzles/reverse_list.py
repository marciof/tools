#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Reverse a linked-list.

Time: O(n)
Space: O(1)
"""

import unittest

class Node:
    def __init__(self, value, nxt = None):
        self.value = value
        self.nxt = nxt

    def to_array(self):
        node = self
        values = []

        while node is not None:
            values.append(node.value)
            node = node.nxt

        return values

def reverse(l):
    previous = None
    current = l

    while current is not None:
        nxt = current.nxt
        current.nxt = previous

        previous = current
        current = nxt

    return previous

class Test (unittest.TestCase):
    def test_reverse_single_node(self):
        l = reverse(Node(1))
        self.assertListEqual(l.to_array(), [1])

    def test_reverse_even_nr_nodes(self):
        l = reverse(Node(1, Node(2)))
        self.assertListEqual(l.to_array(), [2, 1])

    def test_reverse_odd_nr_nodes(self):
        l = reverse(Node(1, Node(2, Node(3))))
        self.assertListEqual(l.to_array(), [3, 2, 1])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
