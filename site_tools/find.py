# -*- coding: UTF-8 -*-


"""
File finder.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


def exists(env):
    return True


def generate(env):
    """
    Adds a *Find* method to the SCons environment.
    """

    env.AddMethod(Find)


def Find(env, target, root = os.path.curdir):
    """
    :param target: file name
    :type target: unicode
    :param root: search starting point path
    :type root: unicode
    :return: file path
    :rtype: unicode
    :raise Exception: file name isn't unique or doesn't exist
    """

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
