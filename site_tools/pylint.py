# -*- coding: UTF-8 -*-


"""
Pylint tool support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_PROGRAM_NAME = 'pylint'
_ENV_NAME = _PROGRAM_NAME.upper()


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``Pylint`` method to the SCons environment.
    """

    env.Tool('which')
    env[_ENV_NAME] = env.Which(_PROGRAM_NAME)
    env.AddMethod(Pylint)


def Pylint(env,
        target = _PROGRAM_NAME,
        source = None,
        root = os.path.curdir,
        config = ''):
    """
    :param target: target name
    :type target: unicode
    :param source: source files to be check, otherwise all sources
    :type source: list
    :param root: search starting point path when ``source`` is unspecified
    :type root: unicode
    :param config: tool configuration file path, otherwise use default
    :type config: unicode
    :return: SCons target
    """

    if source is None:
        env.Tool('globr')
        source = env.Globr('*.py', root = root, exclude_root = True)

    config = os.path.relpath(config, root)
    command = [env[_ENV_NAME], '--rcfile=' + config] + map(str, source)

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([command], source = source, chdir = root)))
