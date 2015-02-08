# -*- coding: UTF-8 -*-


# Standard:
from __future__ import division, print_function, unicode_literals


PROGRAM = 'pylint'


def build(env, target, source, config_file = ''):
    command = [PROGRAM, '--rcfile=' + config_file] + map(str, source)
    
    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([command], source = source)))


def exists(env):
    return env.Detect(PROGRAM)


def generate(env):
    env.AddMethod(build, PROGRAM.title())
