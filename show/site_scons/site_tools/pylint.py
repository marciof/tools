# -*- coding: UTF-8 -*-


PROGRAM = 'pylint'


def build(env, target, source, config = ''):
    command = [PROGRAM, '--rcfile=' + config] + map(str, source)
    return [env.AlwaysBuild(env.Alias(target, action = env.Action([command])))]


def exists(env):
    return env.Detect(PROGRAM)


def generate(env):
    env.AddMethod(build, PROGRAM.title())
