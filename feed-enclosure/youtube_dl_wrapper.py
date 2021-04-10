#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Wraps youtube-dl to add support for uGet as an external downloader.
"""

# stdlib
import asyncio
import os
import os.path
from typing import List
from urllib.parse import urldefrag

# external
from asyncinotify import Inotify, Mask
import youtube_dl
from youtube_dl.downloader.external import _BY_NAME, ExternalFD


class UgetFD (ExternalFD):
    AVAILABLE_OPT = '--version'
    BLOCK_SIZE_BYTES = 512

    @classmethod
    def get_basename(cls):
        return 'uget-gtk'

    def _make_cmd(self, tmpfilename: str, info_dict: dict) -> List[str]:
        """
        https://github.com/ytdl-org/youtube-dl#mandatory-and-optional-metafields
        """

        # Remove the URL fragment since uGet seems to break when given it
        # in the command line.
        (defrag_url, fragment) = urldefrag(info_dict['url'])

        # Split filename into folder and name for uGet command line arguments.
        (folder, filename) = os.path.split(tmpfilename)

        if folder == '':
            folder = os.getcwd()

        cmd = [
            self.get_basename(),
            '--quiet',
            '--filename=' + filename,
            '--folder=' + folder,
            defrag_url,
        ]

        return cmd

    def _call_downloader(self, tmpfilename: str, info_dict: dict) -> int:
        return asyncio.run(self.wait_for_download(tmpfilename, info_dict))

    async def wait_for_download(self, tmpfilename: str, info_dict: dict) -> int:
        expected_size = info_dict.get('filesize')
        (folder, filename) = os.path.split(tmpfilename)

        if folder == '':
            folder = os.getcwd()

        if expected_size is None:
            self.report_warning(
                '[%s] Unknown file size, will track file block size only.'
                % self.get_basename())

        with Inotify() as inotify:
            inotify.add_watch(folder, Mask.CLOSE)
            return_code = super()._call_downloader(tmpfilename, info_dict)

            async for event in inotify:
                if event.path.name != tmpfilename:
                    continue

                stat = os.stat(tmpfilename)
                block_size = stat.st_blocks * self.BLOCK_SIZE_BYTES
                size = stat.st_size

                self.to_screen(
                    '[%s] Downloaded %s block bytes (target %s bytes)'
                    % (self.get_basename(), block_size, expected_size or '?'))

                is_downloaded = (
                    (block_size >= size)
                    and (
                        expected_size is None
                        or size == expected_size))

                if is_downloaded:
                    return return_code


_BY_NAME['uget'] = UgetFD


if __name__ == '__main__':
    youtube_dl.main()
