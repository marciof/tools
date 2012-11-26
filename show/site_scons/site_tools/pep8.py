# -*- coding: UTF-8 -*-


PROGRAM = 'pep8'


def exists(env):
    return env.Detect(PROGRAM)


def generate(env):
    env.Append(BUILDERS = {
        PROGRAM.title(): env.Builder(action = [[PROGRAM, '$SOURCES']])
    })
