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

# external
from asyncinotify import Inotify, Mask
import youtube_dl
from youtube_dl.downloader.external import _BY_NAME, ExternalFD


# TODO: ensure the folder path is absolute since uGet doesn't seem to interpret
#       it correctly when invoked in the command line
def split_folder_filename(path: str) -> Tuple[str, str]:
    (folder, filename) = os.path.split(path)

    if folder == '':
        folder = os.getcwd()

    return (folder, filename)


def get_size_on_disk(path: str, block_size_bytes: int = 512) -> Tuple[int, int]:
    stat = os.stat(path)

    # TODO: detect availability of `st_blocks`
    block_size = stat.st_blocks * block_size_bytes

    return (stat.st_size, block_size)


# TODO: refactor out to its own module, separate from this wrapper script
class UgetFD (ExternalFD):
    """
    https://github.com/ytdl-org/youtube-dl#mandatory-and-optional-metafields
    """

    AVAILABLE_OPT = '--version'

    @classmethod
    def get_basename(cls) -> str:
        return 'uget-gtk'

    def _make_cmd(self, tmpfilename: str, info_dict: dict) -> List[str]:
        (folder, filename) = split_folder_filename(tmpfilename)

        # TODO: use youtube-dl's proxy option/value
        # TODO: use `external_downloader_args`
        cmd = [
            self.get_basename(),
            '--quiet',
            '--filename=' + filename,
            '--folder=' + folder,
        ]

        user_agent = info_dict.get('http_headers', {}).get('User-Agent')

        if user_agent is not None:
            cmd += ['--http-user-agent=' + user_agent]

        return cmd + ['--', info_dict['url']]

    def _call_downloader(self, tmpfilename: str, info_dict: dict) -> int:
        try:
            actual_size = os.path.getsize(tmpfilename)
        except OSError:
            actual_size = None

        # TODO use youtube-dl's continue/restart option
        if actual_size is not None:
            self.report_file_already_downloaded(tmpfilename)

            # TODO: use `filesize_approx` as well?
            expected_size = info_dict.get('filesize')

            if expected_size is None:
                self.report_warning(
                    "[%s] Unknown expected file size, assuming it's complete."
                    % self.get_basename())
            elif expected_size != actual_size:
                self.report_error(
                    "[%s] File size doesn't match expected size: %s bytes"
                    % (self.get_basename(), expected_size))
                self.report_unable_to_resume()
                return 1

            return 0

        return asyncio.run(self.wait_for_download(tmpfilename, info_dict))

    # TODO: too long, refactor
    async def wait_for_download(self, tmpfilename: str, info_dict: dict) -> int:
        (folder, filename) = split_folder_filename(tmpfilename)

        # TODO: use `filesize_approx` as well?
        expected_size = info_dict.get('filesize')

        if expected_size is None:
            self.report_warning(
                '[%s] Unknown file size, will track file block size only.'
                % self.get_basename())

        self.to_screen(
            '[%s] Starting inotify watch on folder: %s (%s bytes expected)' % (
                self.get_basename(),
                folder,
                '?' if expected_size is None else expected_size))

        # TODO: use the `watchdog` package to be platform agnostic
        with Inotify() as inotify:
            # TODO: watch target file only for performance (measure first)
            inotify.add_watch(folder, Mask.ONLYDIR | Mask.CLOSE | Mask.CREATE
                | Mask.MODIFY | Mask.MOVED_TO)

            # TODO: the call below may not always return immediately
            return_code = super()._call_downloader(tmpfilename, info_dict)

            self.to_screen('[%s] Return code: %s'
                % (self.get_basename(), return_code))

            event_count = 0
            event_skipped_count = 0

            async for event in inotify:
                event_count += 1

                if event.path.name != tmpfilename:
                    event_skipped_count += 1
                    continue

                # If the file to be downloaded has been already reserved
                # space on disk, then its apparent size will already be the
                # final size. In that case use the disk block size to get
                # an idea for when its download is complete.
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
                    break

            self.to_screen(
                '[%s] inotify events: %s skipped / %s total' %
                (self.get_basename(), event_skipped_count, event_count))
            return return_code


def register_external_downloader(name: str, klass: Type[ExternalFD]) -> None:
    _BY_NAME[name] = klass


def register_uget_external_downloader() -> None:
    register_external_downloader('uget', UgetFD)


if __name__ == '__main__':
    register_uget_external_downloader()
    youtube_dl.main()
