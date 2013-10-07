# -*- coding: UTF-8 -*-


"""
Single file finder.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


def exists(env):
    return True


def generate(env):
    env.AddMethod(_execute, 'Find')


def _execute(env, target, root = os.path.curdir):
    has_found_path = None

    for path, dirs, files in os.walk(root):
        if target in (dirs + files):
            if has_found_path is None:
                has_found_path = path
            else:
                raise Exception('Non-unique file name: ' + target)

    if has_found_path is None:
        raise Exception('File not found: ' + target)
    else:
        return os.path.join(has_found_path, target)
