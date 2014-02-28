# -*- coding: UTF-8 -*-


"""
Recursive glob.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import itertools
import os
import os.path


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Adds a ``Globr`` method to the SCons environment.
    """

    env.AddMethod(Globr)


def Globr(env, pattern, root = os.path.curdir, exclude_root = False):
    """
    :type pattern: unicode
    :param pattern: glob pattern
    :type root: unicode
    :param root: search starting point path
    :type exclude_root: bool
    :param exclude_root: if true makes paths relative to ``root``
    :rtype: list<unicode>
    :return: matching files
    """

    paths = env.Glob(os.path.join(root, pattern))

    for path, dirs, files in os.walk(root):
        paths.extend(itertools.chain.from_iterable(
            [env.Glob(os.path.join(d, pattern)) for d in dirs]))

    if exclude_root:
        return [os.path.relpath(str(path), root) for path in paths]
    else:
        return paths
