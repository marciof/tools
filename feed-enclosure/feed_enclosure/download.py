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


# TODO youtube-dl detection
#      https://github.com/ytdl-org/youtube-dl/#how-can-i-detect-whether-a-given-url-is-supported-by-youtube-dl
#      https://github.com/ytdl-org/youtube-dl/#embedding-youtube-dl
def main(args: Optional[List[str]] = None) -> Any:
    pass


# TODO tests
# TODO GUI?
#      https://github.com/chriskiehl/Gooey
#      https://github.com/PySimpleGUI/PySimpleGUI
#      https://github.com/alfiopuglisi/guietta
if __name__ == '__main__':
    sys.exit(main())
