# -*- coding: UTF-8 -*-

"""
Project-wide standard logging.
"""

# TODO tests

# stdlib
import logging
from logging import Logger
from logging.handlers import SysLogHandler
import os.path


# TODO detect availability of syslog
# TODO include PID for better tracking of multiple concurrent processes
def create_logger(name: str, syslog_address: str = '/dev/log') -> Logger:
    logger = logging.getLogger('feed_enclosure.' + name)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(name)s [%(levelname)s] %(message)s'))
    logger.addHandler(stream_handler)

    if os.path.exists(syslog_address):
        syslog_handler = SysLogHandler(syslog_address)
        syslog_handler.setLevel(logging.DEBUG)
        syslog_handler.setFormatter(logging.Formatter(
            '%(name)s [%(levelname)s] %(message)s'))
        logger.addHandler(syslog_handler)

    return logger
