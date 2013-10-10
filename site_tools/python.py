# -*- coding: UTF-8 -*-


"""
Virtualenv support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


_ENV_NAME = 'PYTHON'


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Sets the *PYTHON* key in the SCons environment, with support for virtualenv.
    """

    if _ENV_NAME not in env:
        virtualenv_path = os.environ.get('VIRTUAL_ENV')
        paths = None

        if virtualenv_path is not None:
            paths = [os.path.join(virtualenv_path, 'bin')]

        env.Tool('which')
        env[_ENV_NAME] = env.Which('python', paths = paths)
