#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Input: valid sequence of rolls for one game of American Ten-Pin Bowling.
Output: total score for the game.

Glossary:

- line = game
- frame = turn
- roll = try (?)
- throw = try (?)

Rules:

- 1 game = 10 turns
- 1 turn = up to 2 tries

- If on first try of his turn he knocks down all the pins (a strike)
  then turn over and turn score = 10 + num. of pins knocked down in his next 2
  tries

- If in 2 tries he knocks them all down (a spare)
  then turn score = 10 + num. of pins knocked down on his next 1 try

- If in 2 tries he does not knock them all down
  then turn score = num. of pins knocked down in his 2 tries

- If he gets a spare or strike in the last turn
  then gets one or two more tries (part of the same turn), respectively.

  - If the bonus throws knock down all the pins, the process does not repeat:
    the bonus throws are only used to calculate the score of the final turn.
"""

import unittest

_NUM_TURNS = 10
_NUM_PINS = 10


class Error (Exception):
    pass

class GameHasFinishedError (Error):
    pass

class TurnHasFinishedError (Error):
    pass

class _NormalTurnType:
    def is_of(self, turn):
        return True

    def score(self, turn, next_turns):
        return sum(turn.num_pins_per_try)

    @property
    def num_bonus_tries(self):
        return 0

    @property
    def num_tries(self):
        return 2

    def __str__(self):
        return '<%s: tries=%s bonus=%s>' % (
          type(self).__name__,
          self.num_tries,
          self.num_bonus_tries)

class _SpecialTurnType (_NormalTurnType):
    def __init__(self,
             num_tries,
             num_bonus_tries,
             num_next_tries_for_points,
             points):

        self._num_tries = num_tries
        self._num_bonus_tries = num_bonus_tries
        self._num_next_tries_for_points = num_next_tries_for_points
        self._points = points

    def is_of(self, turn):
        num_pins_per_try = turn.num_pins_per_try

        return ((len(num_pins_per_try) >= self._num_tries)
            and (sum(num_pins_per_try[:self._num_tries]) == _NUM_PINS))

    def score(self, turn, next_turns):
        next_tries = turn.num_pins_per_try[self._num_tries:]

        for next_turn in next_turns:
            if len(next_tries) >= self._num_next_tries_for_points:
                break
            next_tries.extend(next_turn.num_pins_per_try)

        return self._points + sum(next_tries[:self._num_next_tries_for_points])

    @property
    def num_bonus_tries(self):
        return self._num_bonus_tries

    @property
    def num_tries(self):
        return self._num_tries

NORMAL_TURN_TYPE = _NormalTurnType()

SPARE_TURN_TYPE = _SpecialTurnType(
    num_tries= 2,
    num_bonus_tries= 1,
    num_next_tries_for_points= 1,
    points = 10)

STRIKE_TURN_TYPE = _SpecialTurnType(
    num_tries= 1,
    num_bonus_tries= 2,
    num_next_tries_for_points= 2,
    points = 10)

class Turn:
    def __init__(self):
        self._num_pins_per_try = []
        self._is_bonus_enabled = False
        self._type = NORMAL_TURN_TYPE

    def add_try(self, num_pins):
        if self.has_finished():
            raise TurnHasFinishedError()

        self._num_pins_per_try.append(num_pins)

        if self._type is NORMAL_TURN_TYPE:
            for turn_type in [SPARE_TURN_TYPE, STRIKE_TURN_TYPE]:
                if turn_type.is_of(self):
                    self._type = turn_type
                    break

    def enable_bonus(self):
        self._is_bonus_enabled = True

    def has_finished(self):
        if self._is_bonus_enabled:
            num_bonus_tries = self._type.num_bonus_tries
        else:
            num_bonus_tries = 0

        return ((self.try_num > (self._type.num_tries + num_bonus_tries))
            or (not self._is_bonus_enabled
                and (self._type is not NORMAL_TURN_TYPE)))

    def score(self, next_turns):
        return self._type.score(self, next_turns)

    def __str__(self):
        return '<turn %s: done=%s try=%s pins=%s type=%s>' % (
            id(self),
            self.has_finished(),
            self.try_num,
            self._num_pins_per_try,
            self._type)

    @property
    def num_pins_per_try(self):
        return list(self._num_pins_per_try)

    @property
    def try_num(self):
        return len(self._num_pins_per_try) + 1

class Game:
    def __init__(self):
        self._turns = [Turn()]

    def add_try(self, num_pins):
        if self.has_finished():
            raise GameHasFinishedError()

        self._current_turn.add_try(num_pins)

        if self._current_turn.has_finished():
            if self.turn_num >= _NUM_TURNS:
                self._current_turn.enable_bonus()
            else:
                self._turns.append(Turn())

    def has_finished(self):
        return ((self.turn_num >= _NUM_TURNS)
            and self._current_turn.has_finished())

    def score(self):
        tally = 0
        turns = list(self._turns)

        while turns:
            turn = turns.pop(0)
            tally += turn.score(turns)

        return tally

    @property
    def _current_turn(self):
        return self._turns[-1]

    @property
    def try_num(self):
        return self._current_turn.try_num

    @property
    def turn_num(self):
        return len(self._turns)

def read_input_num_pins():
    num_pins = None

    while num_pins is None:
        try:
            num_pins = int(input('# pins: '), base = 10)
        except ValueError:
            pass
        else:
            if (num_pins < 0) or (num_pins > _NUM_PINS):
                num_pins = None

        if num_pins is None:
            print('Please enter a valid num. of pins (>= 0, <= %s).' % _NUM_PINS)

    return num_pins

class TestFunctional (unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.assertFalse(self.game.has_finished())

    def tearDown(self):
        self.assertTrue(self.game.has_finished())

    def test_all_misses(self):
        for num_pins in 10 * [9, 0]:
            self.game.add_try(num_pins)

        self.assertEqual(self.game.score(), 90)

    def test_all_spares(self):
        for num_pins in 10 * [5, 5] + [5]:
            self.game.add_try(num_pins)

        self.assertEqual(self.game.score(), 150)

    def test_all_strikes(self):
        for num_pins in 12 * [10]:
            self.game.add_try(num_pins)

        self.assertEqual(self.game.score(), 300)

class TestTurn (unittest.TestCase):
    def new_spare_turn(self):
        turn = Turn()
        turn.add_try(2)
        turn.add_try(8)

        self.assertTrue(turn.has_finished())
        self.assertTrue(SPARE_TURN_TYPE.is_of(turn))

        return turn

    def new_strike_turn(self):
        turn = Turn()
        turn.add_try(10)

        self.assertTrue(turn.has_finished())
        self.assertTrue(STRIKE_TURN_TYPE.is_of(turn))

        return turn

    def setUp(self):
        self.turn = Turn()

        self.assertFalse(self.turn.has_finished())
        self.assertTrue(NORMAL_TURN_TYPE.is_of(self.turn))

        self.assertEqual(self.turn.try_num, 1)
        self.assertEqual(self.turn.score([]), 0)

    def test_normal_turn(self):
        num_pins_per_try = [1, 2]

        for num_pins in num_pins_per_try:
            self.turn.add_try(num_pins)

        self.assertTrue(self.turn.has_finished())
        self.assertTrue(NORMAL_TURN_TYPE.is_of(self.turn))
        self.assertEqual(self.turn.try_num, len(num_pins_per_try) + 1)

        spare = self.new_spare_turn()
        strike = self.new_strike_turn()

        for next_turns in [], [spare], [strike]:
            self.assertEqual(
                self.turn.score(next_turns),
                sum(num_pins_per_try))

    def test_spare_turn(self):
        num_pins_per_try = [7, 3]

        for num_pins in num_pins_per_try:
            self.turn.add_try(num_pins)

        self.assertTrue(self.turn.has_finished())
        self.assertTrue(SPARE_TURN_TYPE.is_of(self.turn))
        self.assertEqual(self.turn.try_num, len(num_pins_per_try) + 1)

        spare = self.new_spare_turn()
        strike = self.new_strike_turn()

        for next_turns in [], [spare], [strike]:
            self.assertEqual(
                self.turn.score(next_turns),
                10 + sum(map(
                    lambda t: t.num_pins_per_try[0],
                    next_turns)))

    def test_strike_turn(self):
        num_pins_per_try = [10]

        for num_pins in num_pins_per_try:
            self.turn.add_try(num_pins)

        self.assertTrue(self.turn.has_finished())
        self.assertTrue(STRIKE_TURN_TYPE.is_of(self.turn))
        self.assertEqual(self.turn.try_num, len(num_pins_per_try) + 1)

        spare = self.new_spare_turn()
        strike = self.new_strike_turn()

        for next_turns in [], [spare], [strike]:
            self.assertEqual(
                self.turn.score(next_turns),
                10 + sum(map(
                    lambda t: sum(t.num_pins_per_try[:2]),
                    next_turns)))

if __name__ == '__main__':
    game = Game()

    while not game.has_finished():
        print('Turn/Try: %s/%s' % (game.turn_num, game.try_num))
        game.add_try(read_input_num_pins())
        print()

    print('Score:', game.score())
