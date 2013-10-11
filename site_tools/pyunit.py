# -*- coding: UTF-8 -*-


"""
Unit testing support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os
import sys

# External:
import unittest2


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a *PyUnit* method to the SCons environment.
    """

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

    # Not using a package as the entry point to support Python 2.6.
    return env.AlwaysBuild(env.Alias(target,
        action = env.Action(
            [[sys.executable,
              '-B',
              '-m',
              'unittest2.__main__',
              'discover',
              '-s',
              root]],
            source = source)))
