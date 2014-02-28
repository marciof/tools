# -*- coding: UTF-8 -*-


"""
line_profiler tool support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_PROGRAM_NAME = 'kernprof'
_ENV_NAME = _PROGRAM_NAME.upper()


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``KernProf`` method to the SCons environment.
    """

    env.Tool('which')
    env[_ENV_NAME] = env.Which(_PROGRAM_NAME, extensions = ['.py'])
    env.AddMethod(KernProf)


def KernProf(env, target = _PROGRAM_NAME, source = None):
    """
    :type target: unicode
    :param target: target name
    :type source: unicode
    :param source: file to profile
    :return: SCons target
    """

    return env.AlwaysBuild(env.Alias(target, action = env.Action([[
        env[_ENV_NAME],
        '-l',
        '-v',
        '-o',
        os.devnull,
        source,
    ]])))
