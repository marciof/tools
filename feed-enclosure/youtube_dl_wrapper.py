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
from typing import List, Optional, Tuple, Type

# external
# FIXME missing type stubs for some external libraries
from asyncinotify import Inotify, Mask  # type: ignore
from unidecode import unidecode
import youtube_dl  # type: ignore
from youtube_dl.downloader.external import _BY_NAME, ExternalFD  # type: ignore


# TODO refactor out to its own module, separate from this wrapper script
class UgetFD (ExternalFD):
    """
    https://github.com/ytdl-org/youtube-dl#mandatory-and-optional-metafields
    """

    AVAILABLE_OPT = '--version'

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

    # FIXME uGet doesn't seem to interpret relative folder paths correctly,
    #       so as a workaround make it absolute
    # TODO avoid being called twice for the temporary filename
    def split_folder_filename(self, path: str) -> Tuple[str, str]:
        (folder, filename) = os.path.split(path)

        if folder == '':
            folder = os.getcwd()

        return (folder, filename)

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

    def temp_name(self, filename: str) -> str:
        """
        Ensure the temporary filename doesn't contain Unicode characters,
        since uGet doesn't seem to handle them properly when invoked via the
        command line.
        """

        non_unicode_filename = unidecode(filename)

        if non_unicode_filename != filename:
            self.warn('Filename contains Unicode, cleaning up: %s',
                      non_unicode_filename)

        return super().temp_name(non_unicode_filename)

    def _make_cmd(self, tmpfilename: str, info_dict: dict) -> List[str]:
        (folder, filename) = self.split_folder_filename(tmpfilename)

        # TODO use youtube-dl's proxy option/value
        # TODO use `external_downloader_args`
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

        try:
            (size, block_size) = self.get_disk_sizes(tmpfilename)
            return_code: Optional[int] = 0
            # TODO refactor duplicate check
            is_downloaded = ((block_size >= size)
                             and ((expected_size is None)
                                  or (size == expected_size)))
        except FileNotFoundError:
            return_code = None
            is_downloaded = False

        if not is_downloaded:
            if return_code is None:
                self.ensure_running()
                return_code = super()._call_downloader(tmpfilename, info_dict)
                self.info('Return code: %s', return_code)
            else:
                self.info('File already exists, waiting for download.')

            asyncio.run(self.wait_for_download(tmpfilename, info_dict))
            return return_code

        # TODO use youtube-dl's continue/restart option
        self.report_file_already_downloaded(tmpfilename)

        if expected_size != size:
            self.error(
                "File size (%s bytes) doesn't match expected: %s bytes",
                size, expected_size)
            self.report_unable_to_resume()
            return 1

        return 0

    async def wait_for_download(self, tmpfilename: str, info_dict: dict):
        (folder, filename) = self.split_folder_filename(tmpfilename)

        # TODO use `filesize_approx` as well?
        expected_size = info_dict.get('filesize')

        self.info('Starting inotify watch on folder: %s (%s bytes expected)',
                  folder, expected_size or '?')

        # TODO use the `watchdog` package to be platform agnostic
        with Inotify() as inotify:
            # TODO watch target file only for performance (measure first)
            inotify.add_watch(folder, Mask.ONLYDIR | Mask.CLOSE | Mask.CREATE
                              | Mask.MODIFY | Mask.MOVED_TO)

            event_count = 0
            event_skipped_count = 0

            async for event in inotify:
                event_count += 1

                # TODO add an optional check, if after starting uGet there's no
                #      inotify event for the target filename then it's
                #      suspicious and flag it?
                if event.path.name != tmpfilename:
                    event_skipped_count += 1
                    continue

                # If the file to be downloaded has been already reserved
                # space on disk, then its apparent size will already be the
                # final size. In that case use the disk block size to get
                # an idea for when its download is complete.
                (size, block_size) = self.get_disk_sizes(tmpfilename)

                # TODO debounce/throttle?
                self.info('[%s] Downloaded %s block bytes',
                          self.format_percent(
                              self.calc_percent(block_size, expected_size)),
                          block_size)

                # TODO refactor duplicate check
                is_downloaded = ((block_size >= size)
                                 and ((expected_size is None)
                                      or (size == expected_size)))

                if is_downloaded:
                    break

            self.info('inotify events: %s skipped / %s total',
                      event_skipped_count, event_count)


def register_external_downloader(name: str, klass: Type[ExternalFD]) -> None:
    _BY_NAME[name] = klass


def register_uget_external_downloader() -> None:
    register_external_downloader('uget', UgetFD)


if __name__ == '__main__':
    register_uget_external_downloader()
    youtube_dl.main()
