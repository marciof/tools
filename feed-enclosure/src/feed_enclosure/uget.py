#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Wraps uGet to add additional functionality and workaround certain issues.
"""

# stdlib
import os
import os.path
import subprocess
import sys
from typing import Callable, List, Optional, Tuple

# external
# FIXME missing type stubs for some external libraries
from asyncinotify import Inotify, Mask  # type: ignore
from unidecode import unidecode


class Uget:

    # FIXME uGet doesn't handle filenames with Unicode characters on the CLI
    def clean_file_name(self, file_name: str) -> str:
        return unidecode(file_name)

    # TODO process uGet options and apply workarounds
    def run(self, executable_name: str, *args) -> int:
        self.ensure_running(executable_name)
        command = self.build_command(executable_name, *args)
        return subprocess.run(args=command).returncode

    def ensure_running(self, executable_name: str) -> None:
        """
        If uGet isn't already running, then starting it up will block execution
        until it exits. To avoid that, ensure it's always running already in
        the background.
        """

        # TODO detect existence of `start_new_session` (it's POSIX specific)
        subprocess.Popen([executable_name, '--quiet'],
                         start_new_session=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    def get_file_disk_sizes(
            self, path: str, block_size_bytes: int = 512) -> Tuple[int, int]:
        """
        Get the reported file size, as well as the actual total block size
        on disk.
        """

        stat = os.stat(path)

        # TODO detect availability of `st_blocks` (it's Unix specific)
        block_size = stat.st_blocks * block_size_bytes

        return (stat.st_size, block_size)

    def is_downloaded(
            self,
            file_name: str,
            file_size: Optional[int],
            progress_cb: Optional[Callable[[int], None]] = None) -> bool:

        # If the file to be downloaded has been already reserved
        # space on disk, then its apparent size will already be the
        # final size. In that case use the disk block size to get
        # an idea for when its download is complete.
        (actual_size, block_size) = self.get_file_disk_sizes(file_name)

        if progress_cb is not None:
            progress_cb(block_size)

        return ((block_size >= actual_size)
                and ((file_size is None) or (actual_size == file_size)))

    def build_command(
            self,
            executable_name: str,
            *args: str,
            url: Optional[str] = None,
            file_name: Optional[str] = None,
            http_user_agent: Optional[str] = None,
            quiet: bool = True) -> List[str]:

        command = [executable_name] + (['--quiet'] if quiet else [])

        if file_name is not None:
            # TODO make folder path absolute for uGet
            (folder, filename) = self.split_folder_file_name(file_name)
            command += ['--filename=' + filename, '--folder=' + folder]

        if http_user_agent is not None:
            command += ['--http-user-agent=' + http_user_agent]

        return command + list(*args) + (['--', url] if url else [])

    def split_folder_file_name(self, path: str) -> Tuple[str, str]:
        (folder, file_name) = os.path.split(path)
        return (folder or os.getcwd(), file_name)

    async def wait_for_download(
            self,
            file_name: str,
            file_size: Optional[int],
            progress_cb: Optional[Callable[[int], None]] = None) -> None:

        (folder, filename) = self.split_folder_file_name(file_name)

        # TODO use the `watchdog` package to be platform agnostic?
        with Inotify() as inotify:
            # TODO watch target file only for performance (measure first)
            inotify.add_watch(folder, Mask.ONLYDIR | Mask.CLOSE | Mask.CREATE
                              | Mask.MODIFY | Mask.MOVED_TO)

            # TODO add an optional check, if after starting uGet there's no
            #      inotify event for the target filename then it's
            #      suspicious and flag it?
            async for event in inotify:
                if event.path.name != file_name:
                    continue
                if self.is_downloaded(file_name, file_size, progress_cb):
                    break


if __name__ == '__main__':
    # TODO refactor out executable name
    sys.exit(Uget().run('uget-gtk', sys.argv[1:]))
