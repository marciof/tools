# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``Which`` method to the SCons environment.
    """

    env.AddMethod(Which)


def Which(env, name, paths = None, extensions = None):
    """
    :type name: unicode
    :param name: program name
    :type paths: list<unicode>
    :param paths: additional paths to search
    :type extensions: list<unicode>
    :param extensions: executable extensions to use when searching on Windows
    :rtype: unicode
    :return: program path
    :raise Exception: program wasn't found
    """

    prog_path = env.Detect(name)

    if prog_path is not None:
        return prog_path

    if paths is None:
        paths = []

    for path_var in ('PATH',):
        path = os.environ.get(path_var)

        if path is not None:
            paths.extend(path.split(os.pathsep))

    prog_path = env.WhereIs(name, path = paths, pathext = extensions)

    if prog_path is not None:
        return prog_path

    raise Exception('Program not found: ' + name)
