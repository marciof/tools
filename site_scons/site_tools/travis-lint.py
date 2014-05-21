# -*- coding: UTF-8 -*-


"""
Travis lint support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os.path


_PROGRAM_NAME = 'travis-lint'
_ENV_NAME = _PROGRAM_NAME.upper().replace('-', '_')


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``TravisLint`` method and ``TRAVIS_CI`` variable to the SCons
    environment.
    """

    env.Tool('which')

    # Currently, only Windows needs this as the batch file won't find the
    # Ruby interpreter otherwise.
    env.AppendENVPath('PATH', os.path.dirname(env.Which('ruby')))

    env[_ENV_NAME] = env.Which(_PROGRAM_NAME)
    env.AddMethod(TravisLint)


def TravisLint(env, target = _PROGRAM_NAME):
    """
    :type target: unicode
    :param target: target name
    :return: SCons target
    """

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([[env[_ENV_NAME]]])))
