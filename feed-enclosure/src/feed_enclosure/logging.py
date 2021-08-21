# -*- coding: UTF-8 -*-

"""
Rebuilds RSS/Atom feeds (in stdin) into RSS (in stdout) so that the "best"
enclosures are chosen. Accepts whatever kinds of feed `feedparser` supports.

Enclosure URLs will also have their associated feed entry title saved in the
URL fragment part as a filename, so downloaders can use it if/when needed.
"""

# stdlib
import logging
from logging import Logger
from logging.handlers import SysLogHandler
import os.path


# TODO detect availability of syslog
def create_logger(name: str, syslog_address: str = '/dev/log') -> Logger:
    logger = logging.getLogger('feed_enclosure.' + name)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(name)s [%(levelname)s] %(message)s'))
    logger.addHandler(stream_handler)

    if os.path.exists(syslog_address):
        syslog_handler = SysLogHandler(syslog_address)
        syslog_handler.setFormatter(logging.Formatter(
            '%(name)s [%(levelname)s] %(message)s'))
        logger.addHandler(syslog_handler)

    return logger
