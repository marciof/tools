#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# stdlib
import os
import sys
from typing import Any

# external
from mypy.main import main as mypy_main


def main() -> Any:
    root_path = os.path.dirname(os.path.dirname(__file__))
    mypy_exit_code = None

    try:
        print('--- Mypy ---')

        mypy_main(
            script_path=None,
            stdout=sys.stdout,
            stderr=sys.stderr,
            args=['--', root_path])
    except SystemExit as error:
        mypy_exit_code = error.code

    return mypy_exit_code


if __name__ == '__main__':
    sys.exit(main())
