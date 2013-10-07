# -*- coding: UTF-8 -*-


"""
PEP8 tool support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_PROGRAM_NAME = 'pep8'


def exists(env):
    return env.Detect(_PROGRAM_NAME)


def generate(env):
    """
    Adds a *Pep8* method to the SCons environment.
    """

    env.AddMethod(Pep8)


def Pep8(env,
        target = _PROGRAM_NAME,
        source = None,
        root = os.path.curdir,
        config = ''):
    """
    :param target: target name
    :type target: unicode
    :param source: source files to check, otherwise all sources
    :type source: list
    :param root: search starting point path when *source* is unspecified
    :type root: unicode
    :param config: tool configuration file path, otherwise use default
    :type config: unicode
    :return: SCons target
    """

    if source is None:
        env.Tool('globr')
        source = env.Globr('*.py', root = root)

    command = [_PROGRAM_NAME, '--config=' + config] + map(str, source)

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([command], source = source)))
