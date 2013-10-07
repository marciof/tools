# -*- coding: UTF-8 -*-


"""
Cython support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals


_PROGRAM_NAME = 'cython'


def exists(env):
    return env.Detect(_PROGRAM_NAME)


def generate(env):
    env.AddMethod(_execute, _PROGRAM_NAME.title())


def _execute(env, target, source, is_embedded = True, do_compilation = False):
    embed = ['--embed'] if is_embedded else []

    if not isinstance(source, list):
        source = [source]

    command = env.Command(target, source,
        [[_PROGRAM_NAME, '--output-file', str(target)]
        + embed
        + map(str, source)])

    if do_compilation:
        env.ParseConfig(['python-config', '--cflags', '--libs'])
        return env.Program(target)
    else:
        return command
