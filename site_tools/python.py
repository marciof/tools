# -*- coding: UTF-8 -*-


"""
Python support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os
import sys


def exists(env):
    return True


def generate(env):
    """
    Appends Python's binary directories to the system's path:

    * Scripts directory
    * executable's directory
    """

    paths = [os.path.join(sys.exec_prefix, 'Scripts')]

    if sys.executable:
        paths.append(os.path.dirname(sys.executable))

    for path in paths:
        env.AppendENVPath('PATH', path)
