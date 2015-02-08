# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


PROGRAM = 'travis-lint'


def execute(env, target = PROGRAM):
    return env.AlwaysBuild(env.Alias(target, action = env.Action([PROGRAM])))


def exists(env):
    return env.Detect(PROGRAM)


def generate(env):
    env_var = 'GEM_PATH'
    
    if env_var in os.environ:
        env.AppendENVPath('PATH', map(
            lambda path: os.path.join(path, 'bin'),
            os.environ[env_var].split(os.pathsep)))
    
    env.AddMethod(execute, PROGRAM.title().replace('-', ''))
