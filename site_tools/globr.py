# -*- coding: UTF-8 -*-


"""
Recursive glob.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import itertools
import os


def exists(env):
    return True


def generate(env):
    env.AddMethod(_execute, 'Globr')


def _execute(env, pattern, root = os.path.curdir, exclude_root = False):
    paths = env.Glob(os.path.join(root, pattern))

    for path, dirs, files in os.walk(root):
        paths.extend(itertools.chain.from_iterable(
            [env.Glob(os.path.join(d, pattern)) for d in dirs]))

    if exclude_root:
        return [os.path.relpath(str(path), root) for path in paths]
    else:
        return paths
