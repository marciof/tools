#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Count and aggregate the number of clicks per domain, and all top-level domains
derived from it. The input is a list of CSV lines, each with the count in the
first column, and the domain in the second column.
"""

from collections import defaultdict
import re
from typing import Dict, Iterable, Iterator
import unittest


def enumerate_domains(domain: str) -> Iterator[str]:
    """
    Time: O(n), where n=number of domain parts
    Space: O(1), assuming tail-call optimization for recursion
    """

    yield domain
    top_domain = re.sub(r'^[^.]+\.', '', domain)

    if len(top_domain) != len(domain):
        yield from enumerate_domains(top_domain)


def count_clicks(count_domain_csv_lines: Iterable[str]) -> Dict[str, int]:
    """
    Time: O(n * m), where n=number of CSV lines, m=number of domain parts
    Space: ditto
    """

    count_per_domain: Dict[str, int] = defaultdict(lambda: 0)

    for count_domain_csv_live in count_domain_csv_lines:
        # TODO use the `csv` module for parsing CSV lines
        (count_str, orig_domain) = count_domain_csv_live.split(',')
        count = int(count_str)

        for domain in enumerate_domains(orig_domain):
            count_per_domain[domain] += count

    return count_per_domain


class Test (unittest.TestCase):
    def test_no_lines(self):
        self.assertEqual(count_clicks([]), {})

    def test_single_line_single_domain(self):
        self.assertEqual(count_clicks(['10,com']), {'com': 10})

    def test_single_line_multiple_domains(self):
        self.assertEqual(count_clicks(['10,www.example.com']), {
            'com': 10,
            'example.com': 10,
            'www.example.com': 10,
        })

    def test_multiple_lines_multiple_domains(self):
        count_domain_csv_lines = [
            '20,example.com',
            '10,www.example.com',
            '30,www.python.org',
            '5,org',
        ]

        self.assertEqual(count_clicks(count_domain_csv_lines), {
            'example.com': 30,
            'com': 30,
            'www.example.com': 10,
            'www.python.org': 30,
            'python.org': 30,
            'org': 35,
        })


if __name__ == '__main__':
    unittest.main(verbosity = 2)
