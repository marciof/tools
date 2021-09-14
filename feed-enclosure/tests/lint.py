# -*- coding: UTF-8 -*-

# stdlib
import os
import sys
from typing import Optional, Tuple

# external
# FIXME missing type stubs for some external libraries
from mypy.main import main as mypy_main
from pycodestyle import StyleGuide, StandardReport  # type: ignore


def main() -> Optional[Tuple[Optional[SystemExit], StandardReport]]:
    root_path = os.path.dirname(os.path.dirname(__file__))
    mypy_exit_error = None

    try:
        print('--- Mypy ---')

        mypy_main(
            script_path=None,
            stdout=sys.stdout,
            stderr=sys.stderr,
            args=['--', root_path])
    except SystemExit as error:
        mypy_exit_error = error

    print()

    print('--- pycodestyle ---')
    style_report = StyleGuide().check_files([root_path])

    if style_report.get_count() == 0:
        style_report = None

    if mypy_exit_error or style_report:
        print()
        return (mypy_exit_error, style_report)
    else:
        return None


if __name__ == '__main__':
    sys.exit(main())
