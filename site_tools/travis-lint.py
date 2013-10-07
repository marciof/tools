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
    env_var = 'GEM_PATH'
    
    if env_var in os.environ:
        env.AppendENVPath('PATH', map(
            lambda path: os.path.join(path, 'bin'),
            os.environ[env_var].split(os.pathsep)))
    
    env.AddMethod(_execute, _PROGRAM_NAME.title().replace('-', ''))


def _execute(env, target = _PROGRAM_NAME):
    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([_PROGRAM_NAME])))
