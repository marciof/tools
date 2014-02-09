# -*- coding: UTF-8 -*-


"""
Unit testing support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os
import sys

# External:
import unittest2


# Not using the package to support Python 2.6. Could use the provided `unit2`
# script instead, but it would require a version check.
_UNITTEST_ENTRY_POINT = 'unittest2.__main__'


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
        root = os.path.curdir):
    """
    :type target: unicode
    :param target: target name
    :type root: unicode
    :param root: search starting point path
    :return: SCons target
    """

    return env.AlwaysBuild(env.Alias(target, action = env.Action([[
        sys.executable,
        '-m',
        _UNITTEST_ENTRY_POINT,
        'discover',
        '-s',
        root,
    ]])))


def PyUnitCoverage(env,
        target = 'pyunit-coverage',
        root = os.path.curdir,
        **kwargs):
    """
    :type target: unicode
    :param target: target name
    :type root: unicode
    :param root: search starting point path
    :param kwargs: additional parameters for the ``Coverage`` tool
    :return: SCons target
    """

    env.Tool('coverage')

    return env.Coverage(
        target = target,
        script = _UNITTEST_ENTRY_POINT,
        args = ['discover', '-s', root],
        is_module = True,
        **kwargs)
