# -*- coding: UTF-8 -*-

"""
Wraps Liferea to add additional functionality.

Changes: (1) command to get the path to the feed list OPML file; (2) command
to enable feed enclosure automatic download; (3) command to set feed
conversion filter.
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
from . import log, opml, os_api


MODULE_DOC = __doc__.strip()


# FIXME fix flag `--mainwindow-state`
#       https://github.com/lwindolf/liferea/issues/447
class Liferea:

    def __init__(self):
        self.logger = log.create_logger('liferea')

        # FIXME add options/commands to Liferea app
        self.ENC_AUTO_DOWNLOAD_COMMAND = 'enc-auto-download'
        self.FEED_LIST_COMMAND = 'feed-list'
        self.FILTER_CMD_COMMAND = 'filter-cmd'

        self.arg_parser = argparse.ArgumentParser(
            description=MODULE_DOC, add_help=False)
        self.arg_help = self.arg_parser.add_argument(
            '-h', '--help', action='store_true', help=argparse.SUPPRESS)

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
            return subprocess.run(['liferea'] + rest_args).returncode

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

        if parsed_kwargs[self.arg_help.dest]:
            rest_args.insert(0, self.arg_help.option_strings[0])
            self.arg_parser.print_help()
            print('\n---\n')

        self.logger.debug('Final arguments: %s', rest_args)
        return (parsed_kwargs, rest_args)

    def modify_feed_list_opml_outline_attrib(
            self, name: str, value: str) \
            -> None:

        feed_list = opml.Opml(self.find_feed_list_opml())
        feed_list.set_feed_outline_attrib(name, value)
        feed_list.save_changes()

    def find_feed_list_opml(self) -> Path:
        return xdg_config_home().joinpath('liferea', 'feedlist.opml')

    def set_feed_conversion_filter(self, command: str) -> None:
        self.modify_feed_list_opml_outline_attrib('filtercmd', command)

    def enable_feed_enclosure_auto_download(self) -> None:
        self.modify_feed_list_opml_outline_attrib('encAutoDownload', 'true')


# TODO tests
if __name__ == '__main__':
    sys.exit(Liferea().main())
