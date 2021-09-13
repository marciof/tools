# -*- coding: UTF-8 -*-

"""
OS-agnostic interface.
"""

# stdlib
import os
from typing import Tuple


EXIT_FAILURE = 1

try:
    EXIT_SUCCESS = os.EX_OK
except AttributeError:
    EXIT_SUCCESS = 0


def stat_sizes(path: str, block_size_bytes: int = 512) -> Tuple[int, int]:
    """
    Get the reported file size and actual total block size on disk, in bytes.
    """

    stat = os.stat(path)

    # TODO detect availability of `st_blocks`
    block_size = stat.st_blocks * block_size_bytes

    return (stat.st_size, block_size)
