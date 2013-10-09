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

    # FIXME: Why isn't `exists` called?
    for paths in (None, 'GEM_PATH', 'PATH'):
        if paths is not None:
            paths = os.environ.get(paths)

            if paths is None:
                continue

        path = env.WhereIs(_PROGRAM_NAME, path = paths)

        if path is not None:
            env.AppendENVPath('PATH', os.path.dirname(path))

    env.AddMethod(TravisLint)


def TravisLint(env, target = _PROGRAM_NAME):
    """
    :param target: target name
    :type target: unicode
    :return: SCons target
    """

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([_PROGRAM_NAME])))
