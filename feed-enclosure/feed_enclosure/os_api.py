# -*- coding: UTF-8 -*-

"""
OS-agnostic interface.
"""

# stdlib
import os


EXIT_FAILURE = 1

try:
    EXIT_SUCCESS = os.EX_OK
except AttributeError:
    EXIT_SUCCESS = 0

WAITPID_NO_OPTIONS = 0
