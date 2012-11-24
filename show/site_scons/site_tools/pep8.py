# -*- coding: UTF-8 -*-


PROGRAM_NAME = 'pep8'


def exists(env):
    return env.Detect(PROGRAM_NAME)


def generate(env):
    env.Append(BUILDERS = {'Pep8': env.Builder(action = [[PROGRAM_NAME, '$SOURCES']])})
