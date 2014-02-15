# -*- coding: UTF-8 -*-


"""
Sphinx build support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os.path


_PROGRAM_NAME = 'sphinx-build'
_ENV_NAME = _PROGRAM_NAME.upper().replace('-', '_')


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``Sphinx`` method to the SCons environment.
    """

    env.Tool('which')
    env[_ENV_NAME] = env.Which(_PROGRAM_NAME)
    env.AddMethod(Sphinx)


def Sphinx(env,
        target = _PROGRAM_NAME,
        source = os.path.curdir,
        output = '_build',
        warning_as_error = True):

    """
    :type target: unicode
    :param target: target name
    :type source: unicode
    :param source: source directory
    :type output: unicode
    :param output: output directory
    :type warning_as_error: bool
    :param warning_as_error: *-W* command line option
    :return: SCons target
    """

    command = [source, output]

    if warning_as_error:
        command.insert(0, '-W')

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([[env[_ENV_NAME]] + command])))
