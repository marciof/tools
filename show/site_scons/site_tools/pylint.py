# -*- coding: UTF-8 -*-


PROGRAM_NAME = 'pylint'


def exists(env):
    return env.Detect(PROGRAM_NAME)


def generate(env):
    env.Append(BUILDERS = {'Pylint': env.Builder(action = [[PROGRAM_NAME, '$SOURCES']])})
