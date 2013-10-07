# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


def execute(env, target, root = os.path.curdir):
    found_path = None
    
    for path, dirs, files in os.walk(root):
        if target in (dirs + files):
            if found_path is None:
                found_path = path
            else:
                raise Exception('Non-unique file name: ' + target)
    
    if found_path is None:
        raise Exception('File not found: ' + target)
    else:
        return os.path.join(found_path, target)


def exists(env):
    return True


def generate(env):
    env.AddMethod(execute, 'Find')
