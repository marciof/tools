# -*- coding: UTF-8 -*-

"""
Wraps the various download tools to pick the most appropriate for downloading
feed enclosures.
"""

# stdlib
import sys
from typing import Any, List, Optional

# internal
from . import log, uget, youtube_dl


MODULE_DOC = __doc__.strip()


def main(args: Optional[List[str]] = None) -> Any:
    pass


# TODO tests
if __name__ == '__main__':
    sys.exit(main())
