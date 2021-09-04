# -*- coding: UTF-8 -*-

"""
Wraps Lifera to add additional functionality.

Changes: (1) command to minimize the window; (2) command to get the path to the
feedlist OPML file; (3) command to enable feed enclosure automatic download;
(4) command to set feed conversion filter.
"""

# stdlib
import argparse
from operator import setitem
from pathlib import Path
import subprocess
from typing import Callable, Iterator, List, Optional, Tuple
from xml.etree.ElementTree import Element

# external
# FIXME missing type stubs for some external libraries
import defusedxml.ElementTree as ElementTree  # type: ignore
from xdg import xdg_config_home  # type: ignore
from Xlib.display import Display  # type: ignore
from Xlib.xobject.drawable import Window  # type: ignore


MODULE_DOC = __doc__.strip()

# FIXME add options/commands to Liferea app
ENC_AUTO_DOWNLOAD_COMMAND = 'enc-auto-download'
FEED_LIST_COMMAND = 'feed-list'
FILTER_CMD_COMMAND = 'filter-cmd'
# TODO reuse flag `--mainwindow-state`?
#      https://github.com/lwindolf/liferea/issues/447
MINIMIZE_WINDOW_COMMAND = 'minimize-window'


def iter_windows() -> Iterator[Window]:
    root_window = Display().screen().root

    for window in root_window.query_tree().children:
        (instance_name, class_name) = window.get_wm_class() or (None, None)

        if instance_name == 'liferea' and class_name == 'Liferea':
            yield window


def modify_opml_outline_rss(
        opml: Path, modify: Callable[[Element], None]) \
        -> str:

    feed_root = None

    for (event, element) in ElementTree.iterparse(opml, {'start'}):
        if feed_root is None:
            feed_root = element
        elif element.tag == 'outline' and element.attrib.get('type') == 'rss':
            modify(element)

    return ElementTree.tostring(feed_root, encoding='unicode')


def find_feed_list_opml() -> Path:
    return xdg_config_home().joinpath('liferea', 'feedlist.opml')


# TODO set feed conversion filter command
def set_feed_conversion_filter(command: str, feed_list_opml: Path) -> None:
    pass


# TODO persist changes to OPML
# TODO add dry-run option?
# TODO raise exception/report stderr/exit status on error
def enable_feed_enclosure_auto_download(feed_list_opml: Path) -> None:
    for _ in iter_windows():
        print('Liferea is currently running, please close it first.')
        break
    else:
        print(modify_opml_outline_rss(
            feed_list_opml,
            lambda rss_outline:
                setitem(rss_outline.attrib, 'encAutoDownload', 'true')))


# TODO minimize window
def minimize_window() -> None:
    for window in iter_windows():
        print(window)


def parse_args(args: Optional[List[str]]) \
        -> Tuple[argparse.Namespace, List[str]]:

    parser = argparse.ArgumentParser(description=MODULE_DOC, add_help=False)
    parser.add_argument(
        '-h', '--help', action='store_true', help=argparse.SUPPRESS)

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
        MINIMIZE_WINDOW_COMMAND, help='minimize window')

    (parsed_args, rest_args) = parser.parse_known_args(args)

    if parsed_args.help:
        rest_args.insert(0, '--help')
        parser.print_help()
        print('\n---\n')

    return (parsed_args, rest_args)


def main(args: Optional[List[str]] = None) -> None:
    (parsed_args, rest_args) = parse_args(args)

    if parsed_args.command_arg == ENC_AUTO_DOWNLOAD_COMMAND:
        enable_feed_enclosure_auto_download(find_feed_list_opml())
    elif parsed_args.command_arg == FEED_LIST_COMMAND:
        print(find_feed_list_opml())
    elif parsed_args.command_arg == FILTER_CMD_COMMAND:
        set_feed_conversion_filter(parsed_args.command, find_feed_list_opml())
    elif parsed_args.command_arg == MINIMIZE_WINDOW_COMMAND:
        minimize_window()
    else:
        subprocess.run(['liferea'] + rest_args)


# TODO logging
# TODO tests, refactor as library?
if __name__ == '__main__':
    main()
