# -*- coding: UTF-8 -*-

"""
Wraps Liferea to add additional functionality.

Changes: (1) option to iconify the window; (2) command to get the path to the
feed list OPML file; (3) command to enable feed enclosure automatic download;
(4) command to set feed conversion filter.
"""

# stdlib
import argparse
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

# external
# FIXME missing type stubs for some external libraries
from xdg import xdg_config_home  # type: ignore

# internal
from . import log, opml, os_api, xlib


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

        self.WINDOW_STATE_ICON = 'x-icon'

        self.arg_parser = argparse.ArgumentParser(
            description=MODULE_DOC, add_help=False)
        self.arg_help = self.arg_parser.add_argument(
            '-h', '--help', action='store_true', help=argparse.SUPPRESS)

        # FIXME fix flag `--mainwindow-state`
        #       https://github.com/lwindolf/liferea/issues/447
        self.arg_main_window_state = self.arg_parser.add_argument(
            '-w', '--mainwindow-state',
            metavar='STATE',
            help="enables STATE of `%s' to `XIconifyWindow' Liferea"
                 % self.WINDOW_STATE_ICON)

        self.cmd_arg_parser = self.arg_parser.add_subparsers(
            dest='command_arg')

        self.cmd_arg_parser.add_parser(
            self.ENC_AUTO_DOWNLOAD_COMMAND,
            help='enable automatic feed enclosure download')
        self.cmd_arg_parser.add_parser(
            self.FEED_LIST_COMMAND, help='print feedlist OPML file path')

        filter_cmd_arg_parser = self.cmd_arg_parser.add_parser(
            self.FILTER_CMD_COMMAND, help='set feed conversion filter command')
        self.arg_filter_cmd_command = filter_cmd_arg_parser.add_argument(
            'command')

    def main(self, args: Optional[List[str]] = None) -> Any:
        (parsed_kwargs, rest_args) = self.parse_args(args)
        command = parsed_kwargs[self.cmd_arg_parser.dest]

        if command is None:
            window_state = parsed_kwargs[self.arg_main_window_state.dest]

            if window_state != self.WINDOW_STATE_ICON:
                return self.run(rest_args)
            else:
                return self.run_iconified(rest_args)

        try:
            if command == self.ENC_AUTO_DOWNLOAD_COMMAND:
                self.enable_feed_enclosure_auto_download()
            elif command == self.FEED_LIST_COMMAND:
                print(self.find_feed_list_opml())
            elif command == self.FILTER_CMD_COMMAND:
                self.set_feed_conversion_filter(
                    parsed_kwargs[self.arg_filter_cmd_command.dest])
            else:
                raise Exception('Unknown command: ' + command)

            return os_api.EXIT_SUCCESS
        except SystemExit:
            raise
        except BaseException as error:
            self.logger.error('Failed to interface Liferea', exc_info=error)
            return os_api.EXIT_FAILURE

    def parse_args(self, args: Optional[List[str]]) \
            -> Tuple[Dict[str, Any], List[str]]:

        (parsed_args, rest_args) = self.arg_parser.parse_known_args(args)
        parsed_kwargs = vars(parsed_args)

        self.logger.debug('Parsed arguments: %s', parsed_args)
        self.logger.debug('Remaining arguments: %s', rest_args)

        if parsed_kwargs[self.arg_main_window_state.dest]:
            window_state = parsed_kwargs[self.arg_main_window_state.dest]

            if window_state != self.WINDOW_STATE_ICON:
                rest_args[0:0] = [
                    self.arg_main_window_state.option_strings[0],
                    window_state,
                ]

        if parsed_kwargs[self.arg_help.dest]:
            rest_args.insert(0, self.arg_help.option_strings[0])
            self.arg_parser.print_help()
            print('\n---\n')

        self.logger.debug('Final arguments: %s', rest_args)
        return (parsed_kwargs, rest_args)

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

    def iconify_window(self) -> None:
        self.xlib.iconify_windows(
            self.XLIB_WINDOW_INSTANCE_NAME, self.XLIB_WINDOW_CLASS_NAME)

    def run(self, args: List[str]) -> int:
        return subprocess.run(['liferea'] + args).returncode

    def run_iconified(self, args: List[str]) -> int:
        if self.is_running():
            return_code = self.run(args)
            self.iconify_window()
            return return_code

        # TODO implement run and iconify
        raise NotImplementedError('Run and iconify not implemented.')

    def find_feed_list_opml(self) -> Path:
        return xdg_config_home().joinpath('liferea', 'feedlist.opml')

    def set_feed_conversion_filter(self, command: str) -> None:
        self.modify_feed_list_opml_outline_attrib('filtercmd', command)

    def enable_feed_enclosure_auto_download(self) -> None:
        self.modify_feed_list_opml_outline_attrib('encAutoDownload', 'true')


# TODO tests
if __name__ == '__main__':
    sys.exit(Liferea().main())
