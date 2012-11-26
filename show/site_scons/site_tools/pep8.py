# -*- coding: UTF-8 -*-


PROGRAM = 'pep8'


def build(env, target, source, config_file = ''):
    command = [PROGRAM, '--config=' + config_file] + map(str, source)

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([command], source = source)))


def exists(env):
    return env.Detect(PROGRAM)


def generate(env):
    env.AddMethod(build, PROGRAM.title())
