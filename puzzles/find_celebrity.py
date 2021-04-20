#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
In a party of one or more people, only one person is known to everyone.
Such a person may be present in the party, if yes, the person doesn't know
anyone in the party. We can only ask questions like "does A know B?".
Find the stranger (celebrity) in minimum number of questions.

Assumption: a person is represented by a consecutive non-negative integer,
starting with zero `0`.
"""

from functools import partial
from typing import Callable, List, Optional
import unittest


KnowsFunction = Callable[[int, int], bool]


def find_celebrity_simple(
        people: List[int],
        knows: KnowsFunction) -> Optional[int]:

    """
    Time: O(n^2)
    Space: O(n)
    """

    if len(people) <= 1:
        return None

    candidates = set(people)

    for person in people:
        for other in people:
            if other == person:
                continue

            if knows(person, other):
                candidates.discard(person)
                break

    if len(candidates) == 1:
        return candidates.pop()
    else:
        return None


def find_celebrity_memory(
        people: List[int],
        knows: KnowsFunction) -> Optional[int]:

    """
    Time: O(n^2)
    Space: O(1)
    """

    if len(people) <= 1:
        return None

    for person in people:
        known_count = 0

        for other in people:
            if other == person:
                continue
            if not knows(other, person):
                break

            known_count += 1

        if known_count == (len(people) - 1):
            is_unknown = True

            for other in people:
                if other == person:
                    continue
                if knows(person, other):
                    is_unknown = False
                    break

            if is_unknown:
                return person

    return None


def knows_matrix(person_1, person_2, known_matrix: List[List[bool]]) -> bool:
    if person_1 == person_2:
        return True
    else:
        return known_matrix[person_1][person_2]


class Test (unittest.TestCase):
    find_impls = {
        find_celebrity_simple,
        find_celebrity_memory,
    }

    def test_all_know_celebrity(self):
        known_matrix = [
            [None, True, True],
            [False, None, False],
            [True, True, None],
        ]

        people = list(range(len(known_matrix)))
        knows = partial(knows_matrix, known_matrix = known_matrix)

        for find_impl in self.find_impls:
            with self.subTest(find_impl):
                self.assertEqual(find_impl(people, knows), 1)

    def test_empty_party(self):
        for find_impl in self.find_impls:
            with self.subTest(find_impl):
                self.assertEqual(find_impl([], lambda: False), None)

    def test_no_known_people(self):
        known_matrix = [
            [None, False, False],
            [False, None, False],
            [False, False, None],
        ]

        people = list(range(len(known_matrix)))
        knows = partial(knows_matrix, known_matrix = known_matrix)

        for find_impl in self.find_impls:
            with self.subTest(find_impl):
                self.assertEqual(find_impl(people, knows), None)

    def test_all_known_people(self):
        known_matrix = [
            [None, True, True],
            [True, None, True],
            [True, True, None],
        ]

        people = list(range(len(known_matrix)))
        knows = partial(knows_matrix, known_matrix = known_matrix)

        for find_impl in self.find_impls:
            with self.subTest(find_impl):
                self.assertEqual(find_impl(people, knows), None)


if __name__ == '__main__':
    unittest.main(verbosity = 2)
