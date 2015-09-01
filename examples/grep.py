#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from __future__ import absolute_import, division, unicode_literals
import sys
import argf


def main(string, invert = False):
    """
    Really simple grep clone.

    :param string: literal text to search for in stdin
    :param invert: show non-matching lines instead
    """

    if string == '':
        raise argf.Error('string to search for must not be empty')

    for line in sys.stdin:
        is_match = string in line

        if (is_match and not invert) or (not is_match and invert):
            print line,


argf.start(main)
