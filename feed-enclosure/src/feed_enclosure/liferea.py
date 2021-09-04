# -*- coding: UTF-8 -*-

"""
Wraps Liferea to add additional functionality.

Changes: (1) command to minimize the window; (2) command to get the path to the
feedlist OPML file; (3) command to enable feed enclosure automatic download;
(4) command to set feed conversion filter.
"""

# stdlib
import argparse
from operator import setitem
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Iterator, List, Optional, Tuple
from xml.etree.ElementTree import Element

# external
# FIXME missing type stubs for some external libraries
import defusedxml.ElementTree as ElementTree  # type: ignore
from xdg import xdg_config_home  # type: ignore
from Xlib.display import Display  # type: ignore
from Xlib.xobject.drawable import Window  # type: ignore

# internal
from . import log


MODULE_DOC = __doc__.strip()


class Liferea:

    def __init__(self):
        self.logger = log.create_logger('liferea')

        # FIXME add options/commands to Liferea app
        self.ENC_AUTO_DOWNLOAD_COMMAND = 'enc-auto-download'
        self.FEED_LIST_COMMAND = 'feed-list'
        self.FILTER_CMD_COMMAND = 'filter-cmd'
        self.MINIMIZE_WINDOW_COMMAND = 'minimize-window'

        self.arg_parser = argparse.ArgumentParser(
            description=MODULE_DOC, add_help=False)
        self.arg_parser.add_argument(
            '-h', '--help', action='store_true', help=argparse.SUPPRESS)

        sub_parsers = self.arg_parser.add_subparsers(dest='command_arg')

        sub_parsers.add_parser(
            self.ENC_AUTO_DOWNLOAD_COMMAND,
            help='enable automatic feed enclosure download')
        sub_parsers.add_parser(
            self.FEED_LIST_COMMAND, help='print feedlist OPML file path')

        filtercmd_parser = sub_parsers.add_parser(
            self.FILTER_CMD_COMMAND, help='set feed conversion filter command')
        filtercmd_parser.add_argument('command')

        sub_parsers.add_parser(
            self.MINIMIZE_WINDOW_COMMAND, help='minimize window')

    def main(self, args: Optional[List[str]] = None) -> Any:
        (parsed_args, rest_args) = self.parse_args(args)

        if parsed_args.command_arg == self.ENC_AUTO_DOWNLOAD_COMMAND:
            self.enable_feed_enclosure_auto_download()
            return None
        elif parsed_args.command_arg == self.FEED_LIST_COMMAND:
            print(self.find_feed_list_opml())
            return None
        elif parsed_args.command_arg == self.FILTER_CMD_COMMAND:
            self.set_feed_conversion_filter(parsed_args.command)
            return None
        elif parsed_args.command_arg == self.MINIMIZE_WINDOW_COMMAND:
            self.minimize_window()
            return None
        else:
            return subprocess.run(['liferea'] + rest_args).returncode

    def parse_args(self, args: Optional[List[str]]) \
            -> Tuple[argparse.Namespace, List[str]]:

        (parsed_args, rest_args) = self.arg_parser.parse_known_args(args)
        self.logger.debug('Parsed arguments: %s', parsed_args)
        self.logger.debug('Remaining arguments: %s', rest_args)

        if parsed_args.help:
            rest_args.insert(0, '--help')
            self.arg_parser.print_help()
            print('\n---\n')

        self.logger.debug('Final arguments: %s', rest_args)
        return (parsed_args, rest_args)

    def iter_windows(self) -> Iterator[Window]:
        root_window = Display().screen().root

        for window in root_window.query_tree().children:
            (instance_name, class_name) = window.get_wm_class() or (None, None)

            if instance_name == 'liferea' and class_name == 'Liferea':
                self.logger.debug('Window: %s', window)
                yield window

    def modify_opml_outline_rss(
            self, opml: Path, modify: Callable[[Element], None]) \
            -> str:

        root = None

        for (event, elem) in ElementTree.iterparse(opml, {'start'}):
            if root is None:
                root = elem
                self.logger.debug('OPML root element: %s', root)
            elif elem.tag == 'outline' and elem.attrib.get('type') == 'rss':
                modify(elem)

        return ElementTree.tostring(root, encoding='unicode')

    def find_feed_list_opml(self) -> Path:
        return xdg_config_home().joinpath('liferea', 'feedlist.opml')

    # TODO set feed conversion filter command
    def set_feed_conversion_filter(self, command: str) -> None:
        pass

    # TODO persist changes to OPML
    # TODO add dry-run option?
    # TODO raise exception/report stderr/exit status on error
    def enable_feed_enclosure_auto_download(self) -> None:
        for _ in self.iter_windows():
            print('Liferea is currently running, please close it first.')
            break
        else:
            print(self.modify_opml_outline_rss(
                self.find_feed_list_opml(),
                lambda rss_outline:
                    setitem(rss_outline.attrib, 'encAutoDownload', 'true')))

    # TODO minimize window
    # TODO reuse flag `--mainwindow-state`?
    #      https://github.com/lwindolf/liferea/issues/447
    def minimize_window(self) -> None:
        for _ in self.iter_windows():
            pass


# TODO tests
if __name__ == '__main__':
    sys.exit(Liferea().main())
