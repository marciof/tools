# -*- coding: UTF-8 -*-

"""
Wraps the various download tools to pick the most appropriate for downloading
feed enclosures.
"""

# stdlib
import argparse
import sys
from typing import Any, List, Optional

# internal
from . import log, uget, youtube_dl


MODULE_DOC = __doc__.strip()


# TODO youtube-dl detection
#      https://github.com/ytdl-org/youtube-dl/#how-can-i-detect-whether-a-given-url-is-supported-by-youtube-dl
#      https://github.com/ytdl-org/youtube-dl/#embedding-youtube-dl
class Download:

    def __init__(self):
        self.logger = log.create_logger('download')

        self.arg_parser = argparse.ArgumentParser(description=MODULE_DOC)
        self.arg_url = self.arg_parser.add_argument(
            'url', help='URL to download')

        self.uget = uget.Uget()
        self.youtube_dl = youtube_dl.YoutubeDl()

    def main(self, args: Optional[List[str]] = None) -> Any:
        parsed_args = self.arg_parser.parse_args(args)
        url = vars(parsed_args)[self.arg_url.dest]
        self.download(url)

    # TODO add folder and filename options
    def download(self, url: str) -> None:
        self.logger.info('Downloading URL: %s', url)

        try:
            self.youtube_dl.download(url)
        except youtube_dl.YoutubeDLError as error:
            self.logger.debug(
                'Failed to download using YouTube DL', exc_info=error)

            # TODO add a uGet `download` method (and wait for it to finish)
            self.uget.main(['--', url])


# TODO tests
# TODO GUI?
#      https://github.com/chriskiehl/Gooey
#      https://github.com/PySimpleGUI/PySimpleGUI
#      https://github.com/alfiopuglisi/guietta
if __name__ == '__main__':
    sys.exit(Download().main())
