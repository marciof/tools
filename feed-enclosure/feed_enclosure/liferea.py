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
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Callable, Iterator, List, Optional, Tuple
from xml.etree.ElementTree import Element

# external
# FIXME missing type stubs for some external libraries
import defusedxml.ElementTree as ElementTree  # type: ignore
from xdg import xdg_config_home  # type: ignore
from Xlib import X, Xutil  # type: ignore
from Xlib.display import Display  # type: ignore
from Xlib.protocol.event import ClientMessage  # type: ignore
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

    def iter_x_windows(self) -> Iterator[Window]:
        display = Display()
        self.logger.debug('X display: %s', display)
        root_window = display.screen().root

        for window in root_window.query_tree().children:
            (instance_name, class_name) = window.get_wm_class() or (None, None)

            if instance_name == 'liferea' and class_name == 'Liferea':
                self.logger.debug('X window: %s', window)
                yield (window, display)

    # TODO iconify window isn't currently working (use python-libxdo?)
    def iconify_x_window(self, display: Display, window: Window) -> None:
        # https://tronche.com/gui/x/xlib/ICC/client-to-window-manager/XIconifyWindow.html
        # https://babbage.cs.qc.cuny.edu/courses/GUIDesign/motif-faq.html

        iconic_state_message = ClientMessage(
            window=window,
            client_type=display.intern_atom('WM_CHANGE_STATE'),
            # TODO named constant for `32`?
            data=(32, [Xutil.IconicState] + 4 * [Xutil.NoValue]))

        self.logger.debug('X iconic state message: %s', iconic_state_message)

        window.send_event(
            event=iconic_state_message,
            event_mask=X.SubstructureNotifyMask | X.SubstructureRedirectMask)

    def is_running(self) -> bool:
        for _ in self.iter_x_windows():
            return True
        else:
            return False

    def modify_opml_outline_rss(
            self, opml: Path, modify: Callable[[Element], None]) \
            -> str:

        root = None
        types = {'rss', 'atom'}

        for (event, elem) in ElementTree.iterparse(opml, {'start'}):
            if root is None:
                root = elem
                self.logger.debug('OPML root element: %s', root)
            elif elem.tag == 'outline' and elem.attrib.get('type') in types:
                modify(elem)

        return ElementTree.tostring(root, encoding='unicode')

    # TODO handle error when Liferea is running
    def modify_feed_list_opml_outline_attrib(
            self, name: str, value: str) \
            -> None:

        if self.is_running():
            raise Exception(
                'Liferea is currently running, please close it first.')

        feed_list_opml_path = self.find_feed_list_opml()

        updated_feed_list_opml = self.modify_opml_outline_rss(
            feed_list_opml_path,
            lambda rss_outline: setitem(rss_outline.attrib, name, value))

        self.logger.debug('Modified feed list OPML outline (%s=%s): %s',
                          name, value, updated_feed_list_opml)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(updated_feed_list_opml)
            f.close()

            self.logger.info('Updating feed list OPML: %s --> %s',
                             f.name, feed_list_opml_path)
            os.replace(f.name, feed_list_opml_path)

    def find_feed_list_opml(self) -> Path:
        return xdg_config_home().joinpath('liferea', 'feedlist.opml')

    # TODO dry-run option?
    # TODO option to apply the same filter cmd to all? useful when adding feeds
    def set_feed_conversion_filter(self, command: str) -> None:
        self.modify_feed_list_opml_outline_attrib('filtercmd', command)

    # TODO dry-run option?
    # TODO option to enable/disable?
    def enable_feed_enclosure_auto_download(self) -> None:
        self.modify_feed_list_opml_outline_attrib('encAutoDownload', 'true')

    # TODO minimize window
    # FIXME fix flag `--mainwindow-state`?
    #       https://github.com/lwindolf/liferea/issues/447
    def minimize_window(self) -> None:
        for (window, display) in self.iter_x_windows():
            self.iconify_x_window(display, window)


# TODO tests
if __name__ == '__main__':
    sys.exit(Liferea().main())
