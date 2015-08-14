#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Standard:
import unittest

# Internal:
import bowling


class TestTurn (unittest.TestCase):
    def new_spare_turn(self):
        turn = bowling.Turn()
        turn.add_try(2)
        turn.add_try(8)

        self.assertTrue(turn.has_finished())
        self.assertTrue(bowling.SPARE_TURN_TYPE.is_of(turn))

        return turn


    def new_strike_turn(self):
        turn = bowling.Turn()
        turn.add_try(10)

        self.assertTrue(turn.has_finished())
        self.assertTrue(bowling.STRIKE_TURN_TYPE.is_of(turn))

        return turn


    def setUp(self):
        self.turn = bowling.Turn()

        self.assertFalse(self.turn.has_finished())
        self.assertTrue(bowling.NORMAL_TURN_TYPE.is_of(self.turn))

        self.assertEqual(self.turn.try_nr, 1)
        self.assertEqual(self.turn.score([]), 0)


    def test_normal_turn(self):
        nr_pins_per_try = [1, 2]

        for nr_pins in nr_pins_per_try:
            self.turn.add_try(nr_pins)

        self.assertTrue(self.turn.has_finished())
        self.assertTrue(bowling.NORMAL_TURN_TYPE.is_of(self.turn))
        self.assertEqual(self.turn.try_nr, len(nr_pins_per_try) + 1)

        spare = self.new_spare_turn()
        strike = self.new_strike_turn()

        for next_turns in [], [spare], [strike]:
            self.assertEqual(
                self.turn.score(next_turns),
                sum(nr_pins_per_try))


    def test_spare_turn(self):
        nr_pins_per_try = [7, 3]

        for nr_pins in nr_pins_per_try:
            self.turn.add_try(nr_pins)

        self.assertTrue(self.turn.has_finished())
        self.assertTrue(bowling.SPARE_TURN_TYPE.is_of(self.turn))
        self.assertEqual(self.turn.try_nr, len(nr_pins_per_try) + 1)

        spare = self.new_spare_turn()
        strike = self.new_strike_turn()

        for next_turns in [], [spare], [strike]:
            self.assertEqual(
                self.turn.score(next_turns),
                10 + sum(map(
                    lambda t: t.nr_pins_per_try[0],
                    next_turns)))


    def test_strike_turn(self):
        nr_pins_per_try = [10]

        for nr_pins in nr_pins_per_try:
            self.turn.add_try(nr_pins)

        self.assertTrue(self.turn.has_finished())
        self.assertTrue(bowling.STRIKE_TURN_TYPE.is_of(self.turn))
        self.assertEqual(self.turn.try_nr, len(nr_pins_per_try) + 1)

        spare = self.new_spare_turn()
        strike = self.new_strike_turn()

        for next_turns in [], [spare], [strike]:
            self.assertEqual(
                self.turn.score(next_turns),
                10 + sum(map(
                    lambda t: sum(t.nr_pins_per_try[:2]),
                    next_turns)))


unittest.main()
