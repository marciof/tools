# -*- coding: UTF-8 -*-

"""
Wraps Liferea to add additional functionality.

Changes: (1) command to minimize the window; (2) command to get the path to the
feedlist OPML file; (3) command to enable feed enclosure automatic download;
(4) command to set feed conversion filter.
"""

# stdlib
import argparse
from pathlib import Path
import subprocess
import sys
from typing import Any, List, Optional, Tuple

# external
# FIXME missing type stubs for some external libraries
from xdg import xdg_config_home  # type: ignore

# internal
from . import log, opml, osi, xlib


MODULE_DOC = __doc__.strip()


class Liferea:

    def __init__(self):
        self.logger = log.create_logger('liferea')

        self.xlib = xlib.Xlib()
        self.XLIB_WINDOW_INSTANCE_NAME = 'liferea'
        self.XLIB_WINDOW_CLASS_NAME = 'Liferea'

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

        if parsed_args.command_arg is None:
            return subprocess.run(['liferea'] + rest_args).returncode

        try:
            if parsed_args.command_arg == self.ENC_AUTO_DOWNLOAD_COMMAND:
                self.enable_feed_enclosure_auto_download()
            elif parsed_args.command_arg == self.FEED_LIST_COMMAND:
                print(self.find_feed_list_opml())
            elif parsed_args.command_arg == self.FILTER_CMD_COMMAND:
                self.set_feed_conversion_filter(parsed_args.command)
            elif parsed_args.command_arg == self.MINIMIZE_WINDOW_COMMAND:
                self.minimize_window()
            else:
                raise Exception('Unknown command: ' + parsed_args.command_arg)

            return osi.EXIT_SUCCESS
        except SystemExit:
            raise
        except BaseException as error:
            self.logger.error('Failed to interface Liferea', exc_info=error)
            return osi.EXIT_FAILURE

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

    def is_running(self) -> bool:
        return self.xlib.has_window(
            self.XLIB_WINDOW_INSTANCE_NAME, self.XLIB_WINDOW_CLASS_NAME)

    def modify_feed_list_opml_outline_attrib(
            self, name: str, value: str) \
            -> None:

        if self.is_running():
            raise Exception(
                'Liferea is currently running, please close it first.')

        feed_list = opml.Opml(self.find_feed_list_opml())
        feed_list.set_feed_outline_attrib(name, value)
        feed_list.save_changes()

    def find_feed_list_opml(self) -> Path:
        return xdg_config_home().joinpath('liferea', 'feedlist.opml')

    def set_feed_conversion_filter(self, command: str) -> None:
        self.modify_feed_list_opml_outline_attrib('filtercmd', command)

    def enable_feed_enclosure_auto_download(self) -> None:
        self.modify_feed_list_opml_outline_attrib('encAutoDownload', 'true')

    # FIXME fix flag `--mainwindow-state`?
    #       https://github.com/lwindolf/liferea/issues/447
    def minimize_window(self) -> None:
        self.xlib.iconify_windows(
            self.XLIB_WINDOW_INSTANCE_NAME, self.XLIB_WINDOW_CLASS_NAME)


# TODO tests
if __name__ == '__main__':
    sys.exit(Liferea().main())
