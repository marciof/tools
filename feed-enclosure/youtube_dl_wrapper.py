#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Wraps youtube-dl to add support for uGet as an external downloader.
"""

# stdlib
import asyncio
import os
import os.path
import subprocess
from time import time
from typing import List, Optional, Tuple, Type

# external
# FIXME missing type stubs for some external libraries
from asyncinotify import Inotify, Mask  # type: ignore
from unidecode import unidecode
import youtube_dl  # type: ignore
from youtube_dl.downloader.external import _BY_NAME, ExternalFD  # type: ignore


# TODO refactor out to its own module, separate from this wrapper script
class UgetFD(ExternalFD):
    """
    https://github.com/ytdl-org/youtube-dl#mandatory-and-optional-metafields
    """

    AVAILABLE_OPT = '--version'
    DOWNLOAD_PROGRESS_THROTTLE_INTERVAL_SEC = 0.5

    @classmethod
    def get_basename(cls) -> str:
        return 'uget-gtk'

    @classmethod
    def ensure_running(cls) -> None:
        """
        If uGet isn't already running, then starting it up will block execution
        until it exits. To avoid that, ensure it's always running already in
        the background.
        """

        # TODO detect existence of `start_new_session` (it's POSIX specific)
        subprocess.Popen([cls.get_basename(), '--quiet'],
                         start_new_session=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    def error(self, message: str, *args) -> None:
        self.report_error(('[%s] ' + message) % (self.get_basename(), *args))

    def info(self, message: str, *args) -> None:
        self.to_screen(('[%s] ' + message) % (self.get_basename(), *args))

    def warn(self, message: str, *args) -> None:
        self.report_warning(('[%s] ' + message) % (self.get_basename(), *args))

    # FIXME uGet misinterprets relative folder paths, so make it absolute
    def split_folder_filename(self, path: str) -> Tuple[str, str]:
        (folder, filename) = os.path.split(path)
        return (folder or os.getcwd(), filename)

    def get_disk_sizes(
            self, path: str, block_size_bytes: int = 512) -> Tuple[int, int]:
        """
        Get the reported file size, as well as the actual total block size
        on disk.
        """

        stat = os.stat(path)

        # TODO detect availability of `st_blocks` (it's Unix specific)
        block_size = stat.st_blocks * block_size_bytes

        return (stat.st_size, block_size)

    # FIXME uGet doesn't handle filenames with Unicode characters on the CLI
    def temp_name(self, filename: str) -> str:
        non_unicode_filename = unidecode(filename)

        if non_unicode_filename != filename:
            self.warn('Filename contains Unicode, cleaning up: %s',
                      non_unicode_filename)

        return super().temp_name(non_unicode_filename)

    def calc_format_percent(self, count: int, total: Optional[int]) -> str:
        return self.format_percent(self.calc_percent(count, total)).strip()

    def is_downloaded(
            self,
            tmpfilename: str,
            info_dict: dict,
            should_log_progress: bool = True) -> bool:

        # TODO use `filesize_approx` as well?
        expected_size = info_dict.get('filesize')

        # If the file to be downloaded has been already reserved
        # space on disk, then its apparent size will already be the
        # final size. In that case use the disk block size to get
        # an idea for when its download is complete.
        (size, block_size) = self.get_disk_sizes(tmpfilename)

        if should_log_progress:
            self.info('Downloaded %s block bytes (%s)',
                      block_size,
                      self.calc_format_percent(block_size, expected_size))

        is_downloaded = ((block_size >= size)
                         and ((expected_size is None)
                              or (size == expected_size)))

        return is_downloaded

    def _make_cmd(self, tmpfilename: str, info_dict: dict) -> List[str]:
        (folder, filename) = self.split_folder_filename(tmpfilename)

        # TODO honor youtube-dl's proxy option/value
        # TODO honor `external_downloader_args`
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
        # TODO use `filesize_approx` as well?
        expected_size = info_dict.get('filesize')

        if expected_size is None:
            self.warn('Unknown expected file size, using block size only.')
        else:
            self.info('Expected file size: %d bytes', expected_size)

        try:
            is_downloaded = self.is_downloaded(
                tmpfilename, info_dict, should_log_progress=False)
            return_code: Optional[int] = 0
        except FileNotFoundError:
            is_downloaded = False
            return_code = None

        # TODO honor youtube-dl's continue/restart option
        if is_downloaded:
            self.report_file_already_downloaded(tmpfilename)
            return 0

        if return_code is None:
            self.ensure_running()
            return_code = super()._call_downloader(tmpfilename, info_dict)
            self.info('Return code: %s', return_code)
        else:
            self.info('File already exists, waiting for download.')

        asyncio.run(self.wait_for_download(tmpfilename, info_dict))
        return return_code

    async def wait_for_download(self, tmpfilename: str, info_dict: dict):
        (folder, filename) = self.split_folder_filename(tmpfilename)
        self.info('Starting inotify watch on folder: %s', folder)

        # TODO use the `watchdog` package to be platform agnostic?
        with Inotify() as inotify:
            # TODO watch target file only for performance (measure first)
            inotify.add_watch(folder, Mask.ONLYDIR | Mask.CLOSE | Mask.CREATE
                              | Mask.MODIFY | Mask.MOVED_TO)

            event_count = 0
            event_skipped_count = 0
            last_timestamp = time()

            # TODO add an optional check, if after starting uGet there's no
            #      inotify event for the target filename then it's
            #      suspicious and flag it?
            async for event in inotify:
                event_count += 1

                if event.path.name != tmpfilename:
                    event_skipped_count += 1
                    continue

                timestamp = time()
                should_log = ((timestamp - last_timestamp)
                              >= self.DOWNLOAD_PROGRESS_THROTTLE_INTERVAL_SEC)

                if self.is_downloaded(tmpfilename, info_dict, should_log):
                    break
                if should_log:
                    last_timestamp = timestamp

            self.info('inotify events: %s skipped / %s total (%s)',
                      event_skipped_count, event_count,
                      self.calc_format_percent(
                          event_skipped_count, event_count))


def register_external_downloader(name: str, klass: Type[ExternalFD]) -> None:
    _BY_NAME[name] = klass


def register_uget_external_downloader() -> None:
    register_external_downloader('uget', UgetFD)


if __name__ == '__main__':
    register_uget_external_downloader()
    youtube_dl.main()
