# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals

# Internal:
import argf


def main(path, user = 'guest', length = 123, verbose = False):
    """
    Some description.

    :type path: int
    :param path: file path
    :param user: user name
    :param length: nr. of elements
    """


argf.start(main, args = ['101', '-u' 'test', '--length', '9', '-v'])
