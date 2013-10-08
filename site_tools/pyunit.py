# -*- coding: UTF-8 -*-


"""
Python's built-in unit tester.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os
import unittest


def exists(env):
    return hasattr(unittest.TestLoader, 'discover')


def generate(env):
    """
    Adds a *PyUnit* method to the SCons environment.
    """

    env.Tool('python')
    env.AddMethod(PyUnit)


def PyUnit(env,
        target = 'pyunit',
        source = None,
        root = os.path.curdir):
    """
    :param target: target name
    :type target: unicode
    :param source: source files to be test, otherwise all test sources
    :type source: list
    :param root: search starting point path when *source* is unspecified
    :type root: unicode
    :return: SCons target
    """

    if source is None:
        env.Tool('globr')
        source = env.Globr('test*.py', root = root)

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action(
            [['python', '-B', '-m', 'unittest', 'discover', '-s', root]],
            source = source)))
