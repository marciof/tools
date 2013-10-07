# -*- coding: UTF-8 -*-


"""
Pylint tool support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_PROGRAM_NAME = 'pylint'


def exists(env):
    return env.Detect(_PROGRAM_NAME)


def generate(env):
    env.AddMethod(_execute, _PROGRAM_NAME.title())


def _execute(env,
        target = _PROGRAM_NAME,
        source = None,
        root = os.path.curdir,
        config = ''):

    if source is None:
        env.Tool('globr')
        source = env.Globr('*.py', root = root, exclude_root = True)

    config = os.path.relpath(config, root)
    command = [_PROGRAM_NAME, '--rcfile=' + config] + map(str, source)

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([command], source = source, chdir = root)))
