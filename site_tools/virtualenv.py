# -*- coding: UTF-8 -*-


"""
Virtualenv support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


def exists(env):
    return env.Detect('virtualenv')


def generate(env):
    """
    Appends the currently active virtualenv binary path to the system's path.
    """

    env_var = 'VIRTUAL_ENV'
    
    if env_var in os.environ:
        env.AppendENVPath('PATH', os.path.join(os.environ[env_var], 'bin'))
