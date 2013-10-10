# -*- coding: UTF-8 -*-


"""
Python's built-in unit tester.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_ENV_NAME = 'python'


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a *PyUnit* method to the SCons environment.
    """

    env.Tool('which')
    env[_ENV_NAME] = env.Which('python')
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
            [[env[_ENV_NAME], '-B', '-m', 'unittest', 'discover', '-s', root]],
            source = source)))
