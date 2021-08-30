# -*- coding: UTF-8 -*-

"""
Wraps Lifera to add additional functionality.

Changes: (1) open Liferea minimized; (2) command to get the path to the
feedlist OPML file; (3) command to enable feed enclosure automatic download;
(4) command to set feed conversion filter.
"""

# stdlib
import argparse
from pathlib import Path
from typing import List, Optional

# external
# FIXME missing type stubs for some external libraries
from xdg import xdg_config_home  # type: ignore


MODULE_DOC = __doc__.strip()
FEED_LIST_COMMAND = 'feed-list'
FILTER_CMD_COMMAND = 'filter-cmd'
# TODO
ENC_AUTO_DOWNLOAD_COMMAND = 'enc-auto-download'


def find_feed_list_opml() -> Path:
    return xdg_config_home().joinpath('liferea', 'feedlist.opml')


# TODO
def set_feed_conversion_filter(command: str, feed_list_opml: Path) -> None:
    pass


def parse_args(args: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=MODULE_DOC)
    sub_parsers = parser.add_subparsers(dest='command_arg')

    sub_parsers.add_parser(
        FEED_LIST_COMMAND, help='print feedlist OPML file path')
    sub_parsers.add_parser(
        ENC_AUTO_DOWNLOAD_COMMAND,
        help='enable automatic feed enclosure download')

    filtercmd_parser = sub_parsers.add_parser(
        FILTER_CMD_COMMAND, help='set feed conversion filter command')
    filtercmd_parser.add_argument('command')

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> None:
    parsed_args = parse_args(args)
    print(parsed_args)

    # FIXME add option/command to Liferea app
    if parsed_args.command_arg == FEED_LIST_COMMAND:
        print(find_feed_list_opml())
    elif parsed_args.command_arg == FILTER_CMD_COMMAND:
        set_feed_conversion_filter(parsed_args.command, find_feed_list_opml())


if __name__ == '__main__':
    main()
