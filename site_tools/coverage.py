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
        is_module = False,
        html_report = None,
        min_coverage = 0):

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
    :type html_report: unicode
    :param html_report: path where to store an HTML report
    :type min_coverage: int
    :param min_coverage: *--fail-under* command line option
    :return: SCons target
    """

    run_command = [env[_ENV_NAME], 'run']
    pyfile = script

    if measure_branch:
        run_command.append('--branch')

    if is_module:
        run_command.append('--module')
        script = None

    if sources is not None:
        run_command.append('--source=' + ','.join(sources))

    run_command.append(pyfile)

    if args is not None:
        run_command.extend(args)

    actions = [env.Action([run_command], source = script)]

    if html_report is not None:
        actions.append(env.Action([[
            env[_ENV_NAME],
            'html',
            '-d',
            html_report,
            '--fail-under=%d' % min_coverage,
        ]]))

    return env.AlwaysBuild(env.Alias(target, action = actions))
