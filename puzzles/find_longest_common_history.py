#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Find the longest common contiguous sequence of URLs between two users' browsing
history. Each user's history is in chronological order, and no URL was visited
more than once.
"""

from typing import List
import unittest


def find_contiguous_history(urls_a: List[str], urls_b: List[str]) -> List[str]:
    """
    Time: O(m * n), where m=number of A URLs, n=number of B URLs
    Space: O(max(m, n)), ditto
    """

    url_b_to_index = {url_b: index for index, url_b in enumerate(urls_b)}
    longest_common_seq = []

    for index_a, url_a in enumerate(urls_a):
        index_b = url_b_to_index.get(url_a)

        if index_b is None:
            continue

        common_seq = [url_a]
        end_index_a = index_a
        end_index_b = index_b

        while True:
            end_index_a += 1
            end_index_b += 1

            if (end_index_a >= len(urls_a)) or (end_index_b >= len(urls_b)):
                break
            if urls_a[end_index_a] != urls_b[end_index_b]:
                break

            common_seq.append(urls_a[end_index_a])

        if len(common_seq) > len(longest_common_seq):
            longest_common_seq = common_seq

    return longest_common_seq


class Test(unittest.TestCase):
    user0 = ["/start", "/green", "/blue", "/pink", "/register", "/orange",
        "/one/two"]
    user1 = ["/start", "/pink", "/register", "/orange", "/red", "a"]
    user2 = ["a", "/one", "/two"]
    user3 = ["/pink", "/orange", "/yellow", "/plum", "/blue", "/tan", "/red",
        "/amber", "/HotRodPink", "/CornflowerBlue", "/LightGoldenRodYellow",
        "/BritishRacingGreen"]
    user4 = ["/pink", "/orange", "/amber", "/BritishRacingGreen", "/plum",
        "/blue", "/tan", "/red", "/lavender", "/HotRodPink", "/CornflowerBlue",
        "/LightGoldenRodYellow"]
    user5 = ["a"]
    user6 = ["/pink", "/orange", "/six", "/plum", "/seven", "/tan", "/red",
        "/amber"]

    def test_empty_history(self):
        self.assertEqual(find_contiguous_history([], []), [])

    def test_case_user0_user1(self):
        self.assertEqual(find_contiguous_history(self.user0, self.user1),
            ["/pink", "/register", "/orange"])

    def test_case_user0_user2(self):
        self.assertEqual(find_contiguous_history(self.user0, self.user2),
            [])

    def test_case_user0_user0(self):
        self.assertEqual(find_contiguous_history(self.user0, self.user0),
            ["/start", "/green", "/blue", "/pink", "/register", "/orange",
                "/one/two"])

    def test_case_user2_user1(self):
        self.assertEqual(find_contiguous_history(self.user2, self.user1),
            ["a"])

    def test_case_user5_user2(self):
        self.assertEqual(find_contiguous_history(self.user5, self.user2),
            ["a"])

    def test_case_user3_user4(self):
        self.assertEqual(find_contiguous_history(self.user3, self.user4),
            ["/plum", "/blue", "/tan", "/red"])

    def test_case_user4_user3(self):
        self.assertEqual(find_contiguous_history(self.user4, self.user3),
            ["/plum", "/blue", "/tan", "/red"])

    def test_case_user3_user6(self):
        self.assertEqual(find_contiguous_history(self.user3, self.user6),
            ["/tan", "/red", "/amber"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
