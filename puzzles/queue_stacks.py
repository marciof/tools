#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Implement a queue using two stacks.
"""

import unittest

# LIFO
class Stack:
    def __init__(self):
        self._data = []

    def is_empty(self):
        return len(self._data) == 0

    def pop(self):
        return self._data.pop()

    def push(self, value):
        self._data.append(value)

# FIFO
class Queue:
    def __init__(self):
        self._in = Stack()
        self._out = Stack()

    def dequeue(self):
        if self._out.is_empty():
            while not self._in.is_empty():
                self._out.push(self._in.pop())

        return self._out.pop()

    def enqueue(self, value):
        self._in.push(value)

    def is_empty(self):
        return self._out.is_empty() and self._in.is_empty()

class Test (unittest.TestCase):
    def setUp(self):
        self.queue = Queue()

    def tearDown(self):
        self.assertTrue(self.queue.is_empty())

    def test_single_element(self):
        self.queue.enqueue(123)
        self.assertEqual(self.queue.dequeue(), 123)

    def test_multiple_elements(self):
        elements = [123, 100, 1, 0]

        for element in elements:
            self.queue.enqueue(element)

        for element in elements:
            self.assertEqual(self.queue.dequeue(), element)

    def test_mix_enqueue_dequeue(self):
        self.queue.enqueue(1)
        self.queue.enqueue(2)
        self.queue.enqueue(3)
        self.assertEqual(self.queue.dequeue(), 1)

        self.queue.enqueue(4)
        self.assertEqual(self.queue.dequeue(), 2)
        self.assertEqual(self.queue.dequeue(), 3)
        self.assertEqual(self.queue.dequeue(), 4)

if __name__ == '__main__':
    unittest.main(verbosity = 2)
