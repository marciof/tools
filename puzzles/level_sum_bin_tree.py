#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Given a binary tree of integers, find the level with the smallest sum of all
the nodes at that level.
"""

import unittest

class Node:
    def __init__(self, value, left = None, right = None):
        self.value = value
        self._left = left
        self._right = right

    def list_children(self):
        if self._left:
            yield self._left

        if self._right:
            yield self._right

def find_level(root):
    queue = [root]

    curr_nr_nodes = 1
    next_nr_nodes = 0

    best_level = 0
    best_sum = float('+inf')

    curr_level = 0
    curr_sum = 0

    while len(queue) > 0:
        node = queue.pop(0)
        curr_sum += node.value
        curr_nr_nodes -= 1

        for child in node.list_children():
            queue.append(child)
            next_nr_nodes += 1

        if curr_nr_nodes == 0:
            curr_nr_nodes = next_nr_nodes
            next_nr_nodes = 0

            if curr_sum < best_sum:
                best_level = curr_level
                best_sum = curr_sum

            curr_level += 1
            curr_sum = 0

    return best_level

class Test (unittest.TestCase):
    def test_single_node(self):
        self.assertEqual(find_level(Node(7)), 0)

    def test_full_tree(self):
        tree = Node(5,
            Node(0,
                Node(-2),
                Node(3)),
            Node(-4))

        self.assertEqual(find_level(tree), 1)

if __name__ == '__main__':
    unittest.main(verbosity = 2)
