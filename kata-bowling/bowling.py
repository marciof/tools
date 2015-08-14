#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Input: valid sequence of rolls for one game of American Ten-Pin Bowling.
# Output: total score for the game.

# Glossary:
#
# - line = game
# - frame = turn
# - roll = try (?)
# - throw = try (?)

# Rules:
#
# - 1 game = 10 turns
# - 1 turn = up to 2 tries
#
# - If on first try of his turn he knocks down all the pins (a strike)
#   then turn over and turn score = 10 + nr. of pins knocked down in his next 2
#   tries
#
# - If in 2 tries he knocks them all down (a spare)
#   then turn score = 10 + nr. of pins knocked down on his next 1 try
#
# - If in 2 tries he does not knock them all down
#   then turn score = nr. of pins knocked down in his 2 tries
#
# - If he gets a spare or strike in the last turn
#   then gets one or two more tries (part of the same turn), respectively.
#
#   - If the bonus throws knock down all the pins, the process does not repeat:
#     the bonus throws are only used to calculate the score of the final turn.


_NR_TURNS = 10
_NR_PINS = 10


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
        return sum(turn.nr_pins_per_try)


    @property
    def nr_bonus_tries(self):
        return 0


    @property
    def nr_tries(self):
        return 2


    def __str__(self):
        return '<%s: tries=%s bonus=%s>' % (
          type(self).__name__,
          self.nr_tries,
          self.nr_bonus_tries)


class _SpecialTurnType (_NormalTurnType):
    def __init__(self,
            nr_tries,
            nr_bonus_tries,
            nr_next_tries_for_points,
            points):

        self._nr_tries = nr_tries
        self._nr_bonus_tries = nr_bonus_tries
        self._nr_next_tries_for_points = nr_next_tries_for_points
        self._points = points


    def is_of(self, turn):
        nr_pins_per_try = turn.nr_pins_per_try

        return ((len(nr_pins_per_try) >= self._nr_tries)
            and (sum(nr_pins_per_try[:self._nr_tries]) == _NR_PINS))


    def score(self, turn, next_turns):
        next_tries = turn.nr_pins_per_try[self._nr_tries:]

        for next_turn in next_turns:
            if len(next_tries) >= self._nr_next_tries_for_points:
                break
            next_tries.extend(next_turn.nr_pins_per_try)

        return self._points + sum(next_tries[:self._nr_next_tries_for_points])


    @property
    def nr_bonus_tries(self):
        return self._nr_bonus_tries


    @property
    def nr_tries(self):
        return self._nr_tries


NORMAL_TURN_TYPE = _NormalTurnType()

SPARE_TURN_TYPE = _SpecialTurnType(
    nr_tries = 2,
    nr_bonus_tries = 1,
    nr_next_tries_for_points = 1,
    points = 10)

STRIKE_TURN_TYPE = _SpecialTurnType(
    nr_tries = 1,
    nr_bonus_tries = 2,
    nr_next_tries_for_points = 2,
    points = 10)


class Turn:
    def __init__(self):
        self._nr_pins_per_try = []
        self._is_bonus_enabled = False
        self._type = NORMAL_TURN_TYPE


    def add_try(self, nr_pins):
        if self.has_finished():
            raise TurnHasFinishedError()

        self._nr_pins_per_try.append(nr_pins)

        if self._type is NORMAL_TURN_TYPE:
            for turn_type in [SPARE_TURN_TYPE, STRIKE_TURN_TYPE]:
                if turn_type.is_of(self):
                    self._type = turn_type
                    break


    def enable_bonus(self):
        self._is_bonus_enabled = True


    def has_finished(self):
        if self._is_bonus_enabled:
            nr_bonus_tries = self._type.nr_bonus_tries
        else:
            nr_bonus_tries = 0

        return ((self.try_nr > (self._type.nr_tries + nr_bonus_tries))
            or (not self._is_bonus_enabled
                and (self._type is not NORMAL_TURN_TYPE)))


    def score(self, next_turns):
        return self._type.score(self, next_turns)


    def __str__(self):
        return '<turn %s: done=%s try=%s pins=%s type=%s>' % (
            id(self),
            self.has_finished(),
            self.try_nr,
            self._nr_pins_per_try,
            self._type)


    @property
    def nr_pins_per_try(self):
        return list(self._nr_pins_per_try)


    @property
    def try_nr(self):
        return len(self._nr_pins_per_try) + 1


class Game:
    def __init__(self):
        self._turns = [Turn()]


    def add_try(self, nr_pins):
        if self.has_finished():
            raise GameHasFinishedError()

        self._current_turn.add_try(nr_pins)

        if self._current_turn.has_finished():
            if self.turn_nr >= _NR_TURNS:
                self._current_turn.enable_bonus()
            else:
                self._turns.append(Turn())


    def has_finished(self):
        return ((self.turn_nr >= _NR_TURNS)
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
    def try_nr(self):
        return self._current_turn.try_nr


    @property
    def turn_nr(self):
        return len(self._turns)


def read_input_nr_pins():
    nr_pins = None

    while nr_pins is None:
        try:
            nr_pins = int(input('# pins: '), base = 10)
        except ValueError:
            pass
        else:
            if (nr_pins < 0) or (nr_pins > _NR_PINS):
                nr_pins = None

        if nr_pins is None:
            print('Please enter a valid nr. of pins (>= 0, <= %s).' % _NR_PINS)

    return nr_pins


if __name__ == '__main__':
    game = Game()

    while not game.has_finished():
        print('Turn/Try: %s/%s' % (game.turn_nr, game.try_nr))
        game.add_try(read_input_nr_pins())
        print()

    print('Score:', game.score())
