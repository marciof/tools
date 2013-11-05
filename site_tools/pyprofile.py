# -*- coding: UTF-8 -*-


"""
Profiling support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os
import pstats
import sys
import tempfile


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``Profile`` method to the SCons environment.
    """

    env.AddMethod(Profile)


def Profile(env,
        target = 'pyprofile',
        source = None,
        callers = True,
        max_entries = 15):

    """
    :type target: unicode
    :param target: target name
    :type source: callable
    :param source: code to profile
    :return: SCons target
    """

    (results_fd, results_path) = tempfile.mkstemp()

    run_profiler = env.Action([[
        sys.executable,
        '-m',
        'cProfile',
        '-o',
        results_path,
        source
    ]])

    def display_results(env, target, source):
        try:
            stats = pstats.Stats(results_path)
            stats.strip_dirs()

            if callers:
                stats.sort_stats('time').print_callers(max_entries)
            else:
                stats.sort_stats('cumulative').print_stats(max_entries)
        finally:
            os.close(results_fd)
            os.remove(results_path)

    return env.AlwaysBuild(env.Alias(target, action = [
        run_profiler,
        env.Action(display_results),
    ]))
