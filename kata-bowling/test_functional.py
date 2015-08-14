#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Standard:
import unittest

# Internal:
import bowling


class TestFronterCases (unittest.TestCase):
    def setUp(self):
        self.game = bowling.Game()
        self.assertFalse(self.game.has_finished())


    def tearDown(self):
        self.assertTrue(self.game.has_finished())


    def test_all_misses(self):
        for nr_pins in 10 * [9, 0]:
            self.game.add_try(nr_pins)

        self.assertEqual(self.game.score(), 90)


    def test_all_spares(self):
        for nr_pins in 10 * [5, 5] + [5]:
            self.game.add_try(nr_pins)

        self.assertEqual(self.game.score(), 150)


    def test_all_strikes(self):
        for nr_pins in 12 * [10]:
            self.game.add_try(nr_pins)

        self.assertEqual(self.game.score(), 300)


unittest.main()
