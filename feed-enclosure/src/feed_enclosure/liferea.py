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


def find_feedlist_opml() -> Path:
    return xdg_config_home().joinpath('liferea', 'feedlist.opml')


def parse_args(args: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=MODULE_DOC)
    sub_parsers = parser.add_subparsers(dest='command')
    sub_parsers.add_parser('feedlist', help='print path to feedlist OPML file')
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> None:
    parsed_args = parse_args(args)

    # FIXME add option/command to Liferea app
    if parsed_args.command == 'feedlist':
        print(find_feedlist_opml())


if __name__ == '__main__':
    main()
