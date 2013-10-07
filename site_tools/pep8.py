# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


PROGRAM = 'pep8'


def execute(env,
        target = PROGRAM,
        source = None,
        root = os.path.curdir,
        config = ''):
    
    if source is None:
        env.Tool('globr')
        source = env.Globr('*.py', root = root)
    
    command = [PROGRAM, '--config=' + config] + map(str, source)
    
    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([command], source = source)))


def exists(env):
    return env.Detect(PROGRAM)


def generate(env):
    env.AddMethod(execute, PROGRAM.title())
