# -*- coding: UTF-8 -*-


# Standard:
from __future__ import division, print_function, unicode_literals


def exists(env):
    try:
        import unittest
        return hasattr(unittest.TestLoader, 'discover')
    except ImportError:
        return False


def generate(env):
    env.Append(BUILDERS = {'UnitTest':
        env.Builder(action = [['python', '-m', 'unittest', 'discover']])})
