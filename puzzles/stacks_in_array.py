#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Implement an API to manipulate 3 different stacks
using a single fixed length array.
"""

import unittest

class OutOfMemoryError (Exception):
    pass

class EmptyError (Exception):
    pass

class Node:
    def __init__(self, value = None, nxt = None, is_empty = False):
        self.value = value
        self.nxt = nxt
        self.is_empty = is_empty

class Stacks:
    def __init__(self, array_length):
        self._array = [Node(is_empty = True) for _ in range(array_length)]
        self._stacks = [None, None, None]

    def push(self, stack, value):
        """
        Time: O(log n), where n=array_length
        """

        for node in self._array:
            if node.is_empty:
                node.is_empty = False
                node.value = value
                node.nxt = self._stacks[stack]

                self._stacks[stack] = node
                break
        else:
            raise OutOfMemoryError()

    def pop(self, stack):
        """
        Time: O(1)
        """

        if self.is_empty(stack):
            raise EmptyError()

        node = self._stacks[stack]
        self._stacks[stack] = node.nxt

        value = node.value

        node.value = None
        node.nxt = None
        node.is_empty = True

        return value

    def is_empty(self, stack):
        return self._stacks[stack] is None

class Test (unittest.TestCase):
    def setUp(self):
        self.stacks = Stacks(4)

    def test_is_empty(self):
        for stack in range(3):
            self.assertTrue(self.stacks.is_empty(stack))

    def test_pop(self):
        for stack in range(3):
            with self.assertRaises(EmptyError):
                self.stacks.pop(stack)

    def test_push(self):
        for stack in range(3):
            self.assertIsNone(self.stacks.push(stack, 'value %s' % stack))

        self.assertIsNone(self.stacks.push(0, 'abc'))

        for stack in range(3):
            with self.assertRaises(OutOfMemoryError):
                self.stacks.push(stack, '123')

    def test_operations_mix(self):
        self.assertIsNone(self.stacks.push(0, 'abc'))
        self.assertFalse(self.stacks.is_empty(0))

        self.assertIsNone(self.stacks.push(1, '123'))
        self.assertFalse(self.stacks.is_empty(1))

        self.assertEqual(self.stacks.pop(0), 'abc')
        self.assertTrue(self.stacks.is_empty(0))

        self.assertIsNone(self.stacks.push(2, '...'))
        self.assertFalse(self.stacks.is_empty(2))

        self.assertEqual(self.stacks.pop(1), '123')
        self.assertTrue(self.stacks.is_empty(1))

if __name__ == '__main__':
    unittest.main(verbosity = 2)
