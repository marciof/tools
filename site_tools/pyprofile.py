# -*- coding: UTF-8 -*-


"""
Python's built-in profiler.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import pstats

try:
    import cProfile as profile
except ImportError:
    import profile

# External:
from SCons.Script import ARGLIST


def exists(env):
    return True


def generate(env):
    """
    Adds a *Profile* method to the SCons environment.
    """

    env.AddMethod(Profile)


def Profile(env, target = 'profile', source = None):
    """
    :param target: target name
    :type target: unicode
    :param source: function to profile
    :type source: callable
    :return: SCons target
    """

    # Store argument for inner function scope.
    actual_source = source

    def execute_profiler(env, target, source):
        args = [value for name, value in ARGLIST if name == '']

        prof = profile.Profile()
        prof.runcall(actual_source, args)

        stats = pstats.Stats(prof)
        stats.strip_dirs().sort_stats('cumulative').print_callers(15)

    return env.AlwaysBuild(env.Alias(target,
        action = env.Action(execute_profiler, source = source)))
