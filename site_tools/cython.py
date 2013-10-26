# -*- coding: UTF-8 -*-


# FIXME
"""
Cython support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals


_PROGRAM_NAME = 'cython'


def exists(env):
    return env.Detect(_PROGRAM_NAME)


def generate(env):
    """
    Adds a ``Cython`` method to the SCons environment.
    """

    env.AddMethod(Cython)


def Cython(env, target, source, is_embedded = True, do_compilation = False):
    """
    :param target: compiled file
    :param source: Python source file
    :type is_embedded: bool
    :param is_embedded: if true passes "--embed" to Cython
    :type do_compilation: bool
    :param do_compilation: if true builds an executable via SCons's ``Program``
    :return: SCons target
    """

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
