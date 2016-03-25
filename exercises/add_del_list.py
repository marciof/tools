#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

class Node:
    def __init__(self, value, next = None):
        self.value = value
        self.next = next

    def to_array(self):
        node = self
        values = []

        while node is not None:
            values.append(node.value)
            node = node.next

        return values

def insert(l, position, value):
    """
    Insert in linked-list.
    """

    if position < 0:
        return None

    previous = None
    current = l
    i = 0

    while (i < position) and (current is not None):
        previous = current
        current = current.next
        i += 1

    if i != position:
        return None

    if previous is None:
        return Node(value, next = l)

    previous.next = Node(value, next = current)
    return l

def delete(l, position):
    """
    Delete from linked-list.
    """

    if position < 0:
        return None

    previous = None
    current = l
    i = 0

    while (i < position) and (current is not None):
        previous = current
        current = current.next
        i += 1

    if i != position:
        return None

    if previous is None:
        return current.next

    previous.next = current.next
    return l

class Test (unittest.TestCase):
    def test_insert_start(self):
        l = insert(Node(1, Node(2, Node(3))), 0, 4)
        self.assertListEqual(l.to_array(), [4, 1, 2, 3])

    def test_insert_middle(self):
        l = insert(Node(1, Node(2, Node(3))), 1, 4)
        self.assertListEqual(l.to_array(), [1, 4, 2, 3])

    def test_insert_end(self):
        l = insert(Node(1, Node(2, Node(3))), 3, 4)
        self.assertListEqual(l.to_array(), [1, 2, 3, 4])

    def test_delete_start(self):
        l = delete(Node(1, Node(2, Node(3))), 0)
        self.assertListEqual(l.to_array(), [2, 3])

    def test_delete_end(self):
        l = delete(Node(1, Node(2, Node(3))), 2)
        self.assertListEqual(l.to_array(), [1, 2])

    def test_delete_middle(self):
        l = delete(Node(1, Node(2, Node(3))), 1)
        self.assertListEqual(l.to_array(), [1, 3])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
