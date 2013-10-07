# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


PROGRAM = 'pylint'


def execute(env,
        target = PROGRAM,
        source = None,
        root = os.path.curdir,
        config = ''):
    
    if source is None:
        env.Tool('globr')
        source = env.Globr('*.py', root = root, exclude_root = True)
    
    config = os.path.relpath(config, root)
    command = [PROGRAM, '--rcfile=' + config] + map(str, source)
    
    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([command], source = source, chdir = root)))


def exists(env):
    return env.Detect(PROGRAM)


def generate(env):
    env.AddMethod(execute, PROGRAM.title())
