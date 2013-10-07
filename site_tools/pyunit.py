# -*- coding: UTF-8 -*-


"""
Python's built-in unit tester.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_BUILDER_NAME = 'PyUnit'


def exists(env):
    try:
        import unittest
        return hasattr(unittest.TestLoader, 'discover')
    except ImportError:
        return False


def generate(env):
    env.AddMethod(_execute, _BUILDER_NAME)


def _execute(env,
        target = _BUILDER_NAME.lower(),
        source = None,
        root = os.path.curdir):

    if source is None:
        env.Tool('globr')
        source = env.Globr('test*.py', root = root)

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action(
            [['python', '-B', '-m', 'unittest', 'discover', '-s', root]],
            source = source)))
