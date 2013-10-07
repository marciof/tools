#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals

# External:
import argf


def main(path, cache = False, timeout = 123):
    """
    Lists a directory.

    :param path: Path to be listed.
    :type path: unicode
    :param cache: Whether or not to cache the list.
    :type cache: bool
    :param timeout: Timeout in seconds.
    :type timeout: int
    """

    print repr([path, cache, timeout])


if __name__ == '__main__':
    argf.start(main)
