#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Insert and delete a node from a linked list.
"""

from typing import List, Optional
import unittest


class Node:
    def __init__(self, value, next: Optional['Node'] = None):
        self.value = value
        self.next = next

    def to_array(self) -> List:
        node: Optional[Node] = self
        values = []

        while node is not None:
            values.append(node.value)
            node = node.next

        return values


def insert(node: Node, position: int, value) -> Optional[Node]:
    """
    Time: O(n)
    Space: O(1)
    """

    if position < 0:
        return None

    previous: Optional[Node] = None
    current: Optional[Node] = node
    i = 0

    while (i < position) and (current is not None):
        previous = current
        current = current.next
        i += 1

    if i != position:
        return None

    if previous is None:
        return Node(value, next=node)

    previous.next = Node(value, next=current)
    return node


def delete(node: Node, position: int) -> Optional[Node]:
    """
    Time: O(n)
    Space: O(1)
    """

    if position < 0:
        return None

    previous: Optional[Node] = None
    current: Optional[Node] = node
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
    return node


class Test (unittest.TestCase):
    def test_insert_start(self):
        lst = insert(Node(1, Node(2, Node(3))), 0, 4)
        self.assertListEqual(lst.to_array(), [4, 1, 2, 3])

    def test_insert_middle(self):
        lst = insert(Node(1, Node(2, Node(3))), 1, 4)
        self.assertListEqual(lst.to_array(), [1, 4, 2, 3])

    def test_insert_end(self):
        lst = insert(Node(1, Node(2, Node(3))), 3, 4)
        self.assertListEqual(lst.to_array(), [1, 2, 3, 4])

    def test_delete_start(self):
        lst = delete(Node(1, Node(2, Node(3))), 0)
        self.assertListEqual(lst.to_array(), [2, 3])

    def test_delete_end(self):
        lst = delete(Node(1, Node(2, Node(3))), 2)
        self.assertListEqual(lst.to_array(), [1, 2])

    def test_delete_middle(self):
        lst = delete(Node(1, Node(2, Node(3))), 1)
        self.assertListEqual(lst.to_array(), [1, 3])


if __name__ == '__main__':
    unittest.main(verbosity=2)
