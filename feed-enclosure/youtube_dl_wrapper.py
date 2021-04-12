#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Wraps youtube-dl to add support for uGet as an external downloader.
"""

# stdlib
import asyncio
import os
import os.path
from typing import List, Tuple, Type
from urllib.parse import urldefrag

# external
from asyncinotify import Inotify, Mask
import youtube_dl
from youtube_dl.downloader.external import _BY_NAME, ExternalFD


def split_folder_filename(path: str) -> Tuple[str, str]:
    (folder, filename) = os.path.split(path)

    if folder == '':
        folder = os.getcwd()

    return (folder, filename)


def get_size_on_disk(path: str, block_size_bytes: int = 512) -> Tuple[int, int]:
    stat = os.stat(path)
    block_size = stat.st_blocks * block_size_bytes
    return (stat.st_size, block_size)


class UgetFD (ExternalFD):
    """
    https://github.com/ytdl-org/youtube-dl#mandatory-and-optional-metafields
    """

    AVAILABLE_OPT = '--version'

    @classmethod
    def get_basename(cls) -> str:
        return 'uget-gtk'

    def _make_cmd(self, tmpfilename: str, info_dict: dict) -> List[str]:
        # Remove the URL fragment since uGet seems to break when given it
        # in the command line.
        (defrag_url, fragment) = urldefrag(info_dict['url'])

        (folder, filename) = split_folder_filename(tmpfilename)

        cmd = [
            self.get_basename(),
            '--quiet',
            '--filename=' + filename,
            '--folder=' + folder,
            defrag_url,
        ]

        return cmd

    def _call_downloader(self, tmpfilename: str, info_dict: dict) -> int:
        # uGet won't overwrite the file if it already exists.
        if os.path.exists(tmpfilename):
            self.report_file_already_downloaded(tmpfilename)
            expected_size = info_dict.get('filesize')

            if expected_size is None:
                self.report_warning(
                    "[%s] Unknown expected file size, assuming it's complete."
                    % self.get_basename())
            elif expected_size != os.path.getsize(tmpfilename):
                self.report_warning(
                    "[%s] File size doesn't match expected size: %s bytes"
                    % (self.get_basename(), expected_size))
                self.report_unable_to_resume()
                return 1

            return 0

        return asyncio.run(self.wait_for_download(tmpfilename, info_dict))

    async def wait_for_download(self, tmpfilename: str, info_dict: dict) -> int:
        (folder, filename) = split_folder_filename(tmpfilename)
        expected_size = info_dict.get('filesize')

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

                # If the file to be downloaded has been already reserved
                # space on disk, then its apparent size will already be the
                # final size. In that case rely on the disk block size to get
                # an idea for when it's fully downloaded.
                (size, block_size) = get_size_on_disk(tmpfilename)

                if (expected_size is None) or (expected_size <= 0):
                    percent = '?'
                else:
                    percent = int(block_size / expected_size * 100)

                self.to_screen(
                    '[%s] Downloaded %s block bytes (~%s%%, target %s bytes)' %
                    (self.get_basename(), block_size, percent,
                     expected_size or '?'))

                is_downloaded = (
                    (block_size >= size)
                    and (
                        expected_size is None
                        or size == expected_size))

                if is_downloaded:
                    return return_code


def register_external_downloader(name: str, klass: Type[ExternalFD]) -> None:
    _BY_NAME[name] = klass


def register_uget_external_downloader() -> None:
    register_external_downloader('uget', UgetFD)


if __name__ == '__main__':
    register_uget_external_downloader()
    youtube_dl.main()
