# -*- coding: UTF-8 -*-


"""
Unit testing support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import sys


try:
    import unittest2 as unittest
except ImportError:
    import unittest


# Not using the package to support Python 2.6. Could use the provided `unit2`
# script instead, but it would require a version check.
_UNITTEST_ENTRY_POINT = unittest.__name__ + '.__main__'


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds ``PyUnit`` and ``PyUnitCoverage`` methods to the SCons environment.
    """

    env.AddMethod(PyUnit)
    env.AddMethod(PyUnitCoverage)


def PyUnit(env,
        target = 'pyunit',
        root = None,
        pattern = None):

    """
    :type target: unicode
    :param target: target name
    :type root: unicode
    :param root: *-s* command line option
    :type pattern: unicode
    :param pattern: *-p* command line option
    :return: SCons target
    """

    command = [sys.executable, '-m', _UNITTEST_ENTRY_POINT, 'discover']

    if root is not None:
        command.extend(['-s', root])

    if pattern is not None:
        command.extend(['-p', pattern])

    return env.AlwaysBuild(env.Alias(target, action = env.Action([command])))


def PyUnitCoverage(env,
        target = 'pyunit-coverage',
        root = None,
        pattern = None,
        **kwargs):

    """
    :type target: unicode
    :param target: target name
    :type root: unicode
    :param root: unittest2 *-s* command line option
    :type pattern: unicode
    :param pattern: unittest2 *-p* command line option
    :param kwargs: additional parameters for the ``Coverage`` tool
    :return: SCons target
    """

    args = ['discover']

    if root is not None:
        args.extend(['-s', root])

    if pattern is not None:
        args.extend(['-p', pattern])

    env.Tool('coverage_py')

    return env.Coverage(
        target = target,
        script = _UNITTEST_ENTRY_POINT,
        args = args,
        is_module = True,
        **kwargs)
