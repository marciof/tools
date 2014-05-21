# -*- coding: UTF-8 -*-


"""
Python environment support.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


# Not called, but required.
def exists(env):
    raise NotImplementedError()


def generate(env):
    """
    Propagates the following Python environment variables to SCons:

    * ``PYTHONDONTWRITEBYTECODE``
    """

    for var in ('PYTHONDONTWRITEBYTECODE',):
        if (var in os.environ) and (var not in env['ENV']):
            env['ENV'][var] = os.environ[var]
