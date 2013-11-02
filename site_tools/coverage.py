# -*- coding: UTF-8 -*-


"""
Coverage.py tool support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals

# External:
import coverage


_PROGRAM_NAME = 'coverage'
_ENV_NAME = _PROGRAM_NAME.upper()


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``Coverage`` method to the SCons environment.
    """

    env.Tool('which')
    env[_ENV_NAME] = env.Which(_PROGRAM_NAME)
    env.AddMethod(Coverage)


def Coverage(env,
        target = _PROGRAM_NAME,
        script = None,
        args = None,
        sources = None,
        measure_branch = False,
        is_module = False):

    """
    :type target: unicode
    :param target: target name
    :type script: unicode
    :param script: file to execute
    :type args: list
    :param args: script arguments
    :type sources: list
    :param sources: *--source* command line option
    :type measure_branch: bool
    :param measure_branch: *--branch* command line option
    :type is_module: bool
    :param is_module: *--module* command line option
    :return: SCons target
    """

    command = [env[_ENV_NAME], 'run']
    pyfile = script

    if measure_branch:
        command.append('--branch')

    if is_module:
        command.append('--module')
        script = None

    if sources is not None:
        command.append('--source=' + ','.join(sources))

    command.append(pyfile)

    if args is not None:
        command.extend(args)

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action([command], source = script)))
