#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Wraps youtube-dl to add support for uGet as an external downloader.
"""

# stdlib
import asyncio
from time import time
from typing import List, Optional, Type

# external
# FIXME missing type stubs for some external libraries
import youtube_dl  # type: ignore
from youtube_dl.downloader.external import _BY_NAME, ExternalFD  # type: ignore

# internal
from . import uget


class UgetFD(ExternalFD):
    """
    https://github.com/ytdl-org/youtube-dl#mandatory-and-optional-metafields
    """

    AVAILABLE_OPT = '--version'

    def __init__(
            self,
            *args,
            download_progress_throttle_interval_sec: float = 0.5,
            **kwargs):

        super().__init__(*args, **kwargs)
        self.uget = uget.Uget()
        self.last_timestamp = time()
        self.download_progress_throttle_interval_sec = \
            download_progress_throttle_interval_sec

    @classmethod
    def get_basename(cls) -> str:
        return 'uget-gtk'

    def error(self, message: str, *args) -> None:
        self.report_error(('[%s] ' + message) % (self.get_basename(), *args))

    def info(self, message: str, *args) -> None:
        self.to_screen(('[%s] ' + message) % (self.get_basename(), *args))

    def warn(self, message: str, *args) -> None:
        self.report_warning(('[%s] ' + message) % (self.get_basename(), *args))

    def log_progress_throttled(
            self, current_size: int, expected_size: Optional[int]):

        timestamp = time()
        should_log = ((timestamp - self.last_timestamp)
                      >= self.download_progress_throttle_interval_sec)

        if should_log:
            self.last_timestamp = timestamp
            self.info('Downloaded %s block bytes (%s)',
                      current_size,
                      self.calc_format_percent(current_size, expected_size))

    def temp_name(self, filename: str) -> str:
        clean_file_name = self.uget.clean_file_name(filename)

        if clean_file_name != filename:
            self.warn('Filename cleaned up: %s', clean_file_name)

        return super().temp_name(clean_file_name)

    def calc_format_percent(self, count: int, total: Optional[int]) -> str:
        return self.format_percent(self.calc_percent(count, total)).strip()

    def _make_cmd(self, tmpfilename: str, info_dict: dict) -> List[str]:
        # TODO honor youtube-dl's proxy option/value
        # TODO honor `external_downloader_args`
        return self.uget.make_command(
            self.get_basename(),
            info_dict['url'],
            file_name=tmpfilename,
            http_user_agent=info_dict.get('http_headers', {})
                .get('User-Agent'))

    def _call_downloader(self, tmpfilename: str, info_dict: dict) -> int:
        # TODO use `filesize_approx` as well?
        expected_size = info_dict.get('filesize')

        if expected_size is None:
            self.warn('Unknown expected file size, using block size only.')
        else:
            self.info('Expected file size: %d bytes', expected_size)

        try:
            is_downloaded = self.uget.is_downloaded(tmpfilename, expected_size)
            return_code: Optional[int] = 0
        except FileNotFoundError:
            is_downloaded = False
            return_code = None

        # TODO honor youtube-dl's continue/restart option
        if is_downloaded:
            self.report_file_already_downloaded(tmpfilename)
            return 0

        if return_code is None:
            self.uget.ensure_running(self.get_basename())
            return_code = super()._call_downloader(tmpfilename, info_dict)
            self.info('Return code: %s', return_code)
        else:
            self.info('File already exists, waiting for download.')

        asyncio.run(self.wait_for_download(tmpfilename, info_dict))
        return return_code

    async def wait_for_download(self, tmpfilename: str, info_dict: dict):
        expected_size = info_dict.get('filesize')

        await self.uget.wait_for_download(
            tmpfilename,
            expected_size,
            lambda current_size:
                self.log_progress_throttled(current_size, expected_size))


def register_external_downloader(name: str, klass: Type[ExternalFD]) -> None:
    _BY_NAME[name] = klass


def register_uget_external_downloader() -> None:
    register_external_downloader('uget', UgetFD)


if __name__ == '__main__':
    register_uget_external_downloader()
    youtube_dl.main()
