# -*- coding: UTF-8 -*-

# TODO documentation
"""
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


def parse_args(args: Optional[List[str]]) -> None:
    parser = argparse.ArgumentParser(description=MODULE_DOC)
    parser.parse_args(args)


# TODO add sub-commands
# TODO replace shell script
def main(args: Optional[List[str]] = None) -> None:
    parse_args(args)
    print(find_feedlist_opml())


if __name__ == '__main__':
    main()
