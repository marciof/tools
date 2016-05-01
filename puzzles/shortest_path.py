#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import collections
import unittest

Road = collections.namedtuple('Road', ['houses', 'inter_a', 'inter_b'])

class Intersect:
    def __init__(self, name):
        self.name = name
        self.roads = []

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)

def shortest_path(start, house):
    """
    Find shortest path from road `start` to a road containing `house` nr.

    https://en.wikipedia.org/wiki/Breadth-first_search

    Time: O(V+E)
    """

    prev_by_road = {start: None}
    queue = [start]

    while len(queue) > 0:
        current_road = queue.pop(0)

        if house in current_road.houses:
            path = []

            while current_road is not None:
                path.insert(0, current_road)
                current_road = prev_by_road[current_road]

            return path

        for inter in (current_road.inter_a, current_road.inter_b):
            if inter is not None:
                for next_road in inter.roads:
                    if next_road not in prev_by_road:
                        prev_by_road[next_road] = current_road
                        queue.append(next_road)

    return None

class TestMapInvertedA (unittest.TestCase):
    def setUp(self):
        self.NW_inter = Intersect('NW')
        self.SW_inter = Intersect('SW')
        self.NE_inter = Intersect('NE')
        self.SE_inter = Intersect('SE')

        self.NW_road = Road(
            houses = (1, 2, 3),
            inter_a = None,
            inter_b = self.NW_inter)

        self.NW_inter.roads.append(self.NW_road)

        self.SW_road = Road(
            houses = (4, 5),
            inter_a = self.NW_inter,
            inter_b = self.SW_inter)

        self.NW_inter.roads.append(self.SW_road)
        self.SW_inter.roads.append(self.SW_road)

        self.N_road = Road(
            houses = (6,),
            inter_a = self.NW_inter,
            inter_b = self.NE_inter)

        self.NW_inter.roads.append(self.N_road)
        self.NE_inter.roads.append(self.N_road)

        self.S_road = Road(
            houses = (7, 8, 9, 10),
            inter_a = self.SW_inter,
            inter_b = self.SE_inter)

        self.SW_inter.roads.append(self.S_road)
        self.SE_inter.roads.append(self.S_road)

        self.NE_road = Road(
            houses = (11,),
            inter_a = None,
            inter_b = self.NE_inter)

        self.NE_inter.roads.append(self.NE_road)

        self.SE_road = Road(
            houses = (12,),
            inter_a = self.NE_inter,
            inter_b = self.SE_inter)

        self.NE_inter.roads.append(self.SE_road)
        self.SE_inter.roads.append(self.SE_road)

    def test_from_north_west_to_north_east(self):
        self.assertListEqual(
            shortest_path(self.NW_road, 11),
            [self.NW_road, self.N_road, self.NE_road])

    def test_from_north_east_to_south_east(self):
        self.assertListEqual(
            shortest_path(self.NE_road, 12),
            [self.NE_road, self.SE_road])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
