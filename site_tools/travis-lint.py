# -*- coding: UTF-8 -*-


"""
Travis lint support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_PROGRAM_NAME = 'travis-lint'


def exists(env):
    return env.Detect(_PROGRAM_NAME)


def generate(env):
    """
    Adds a *TravisLint* method to the SCons environment.
    """

    env_var = 'GEM_PATH'
    
    if env_var in os.environ:
        env.AppendENVPath('PATH', map(
            lambda path: os.path.join(path, 'bin'),
            os.environ[env_var].split(os.pathsep)))
    
    env.AddMethod(TravisLint)


def TravisLint(env, target = _PROGRAM_NAME):
    """
    :param target: target name
    :type target: unicode
    :return: SCons target
    """

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([_PROGRAM_NAME])))
