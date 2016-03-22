#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import random
import unittest

def pick_random(array, count):
    """
    Pick `count` randomly selected items from `array`.
    """

    if not array or (count <= 0):
        return []

    shuffled = {}
    elements = []

    for i in range(0, len(array) - 1):
        if len(elements) == count:
            return elements

        j = random.randint(i, len(array) - 1)

        elem_i = shuffled.get(i, array[i])
        elem_j = shuffled.get(j, array[j])

        shuffled[i] = elem_j
        shuffled[j] = elem_i

        elements.append(shuffled.pop(i))

    elements.append(shuffled.pop(len(array) - 1, array[-1]))
    return elements

class Test (unittest.TestCase):
    def test_empty_array(self):
        self.assertEqual(
            pick_random([], 3),
            [])

    def test_no_elements(self):
        self.assertEqual(
            pick_random(list('example'), 0),
            [])

    def test_all_elements(self):
        self.assertCountEqual(
            pick_random(list('example'), 7),
            'example')

    def test_more_elements_than_array(self):
        self.assertCountEqual(
            pick_random(list('example'), 100),
            'example')

    def test_some_elements(self):
        array = list('example')
        elements = pick_random(array, 3)

        self.assertEqual(len(elements), 3)

        for element in elements:
            self.assertIn(element, array)

if __name__ == '__main__':
    unittest.main(verbosity = 2)
