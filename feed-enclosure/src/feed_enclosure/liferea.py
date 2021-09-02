# -*- coding: UTF-8 -*-

"""
Wraps Lifera to add additional functionality.

Changes: (1) minimize Liferea's window; (2) command to get the path to the
feedlist OPML file; (3) command to enable feed enclosure automatic download;
(4) command to set feed conversion filter.
"""

# stdlib
import argparse
from pathlib import Path
import subprocess
from typing import List, Optional, Tuple

# external
# FIXME missing type stubs for some external libraries
import defusedxml.ElementTree as DefusedElementTree  # type: ignore
from xdg import xdg_config_home  # type: ignore


MODULE_DOC = __doc__.strip()

# FIXME add options/commands to Liferea app
ENC_AUTO_DOWNLOAD_COMMAND = 'enc-auto-download'
FEED_LIST_COMMAND = 'feed-list'
FILTER_CMD_COMMAND = 'filter-cmd'
MINIMIZE_COMMAND = 'minimize'


def find_feed_list_opml() -> Path:
    return xdg_config_home().joinpath('liferea', 'feedlist.opml')


# TODO set feed conversion filter command
def set_feed_conversion_filter(command: str, feed_list_opml: Path) -> None:
    pass


# TODO enable feed enclosure automatic download
def enable_feed_enclosure_auto_download(feed_list_opml: Path) -> None:
    pass


# TODO minimize window
def minimize_window() -> None:
    pass


# TODO handle help flag
def parse_args(args: Optional[List[str]]) \
        -> Tuple[argparse.Namespace, List[str]]:

    parser = argparse.ArgumentParser(description=MODULE_DOC)
    sub_parsers = parser.add_subparsers(dest='command_arg')

    sub_parsers.add_parser(
        ENC_AUTO_DOWNLOAD_COMMAND,
        help='enable automatic feed enclosure download')
    sub_parsers.add_parser(
        FEED_LIST_COMMAND, help='print feedlist OPML file path')

    filtercmd_parser = sub_parsers.add_parser(
        FILTER_CMD_COMMAND, help='set feed conversion filter command')
    filtercmd_parser.add_argument('command')

    sub_parsers.add_parser(
        MINIMIZE_COMMAND, help='run in the background minimized')

    return parser.parse_known_args(args)


def main(args: Optional[List[str]] = None) -> None:
    (parsed_args, rest_args) = parse_args(args)

    if parsed_args.command_arg == ENC_AUTO_DOWNLOAD_COMMAND:
        enable_feed_enclosure_auto_download(find_feed_list_opml())
    elif parsed_args.command_arg == FEED_LIST_COMMAND:
        print(find_feed_list_opml())
    elif parsed_args.command_arg == FILTER_CMD_COMMAND:
        set_feed_conversion_filter(parsed_args.command, find_feed_list_opml())
    elif parsed_args.command_arg == MINIMIZE_COMMAND:
        minimize_window()
    else:
        subprocess.run(['liferea'] + rest_args)


if __name__ == '__main__':
    main()
