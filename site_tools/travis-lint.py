# -*- coding: UTF-8 -*-


"""
Travis lint support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_PROGRAM_NAME = 'travis-lint'
_ENV_NAME = _PROGRAM_NAME.upper().replace('-', '_')
_TRAVIS_CI_ENV_NAME = 'TRAVIS_CI'


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``TravisLint`` method to the SCons environment.
    """

    env[_TRAVIS_CI_ENV_NAME] = ((os.environ.get('CI') == 'true')
        and (os.environ.get('TRAVIS') == 'true'))

    if not env[_TRAVIS_CI_ENV_NAME]:
        env.Tool('which')
        env[_ENV_NAME] = env.Which(_PROGRAM_NAME)

    env.AddMethod(TravisLint)


def TravisLint(env, target = _PROGRAM_NAME):
    """
    :param target: target name
    :type target: unicode
    :return: SCons target
    """

    if env[_TRAVIS_CI_ENV_NAME]:
        def action(*args, **kwargs):
            pass
    else:
        action = [[env[_ENV_NAME]]]

    return env.AlwaysBuild(env.Alias(target, action = env.Action(action)))
