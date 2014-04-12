# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import glob
import itertools
import sys

# External:
import pkg_resources

# Internal:
import setupext.cmd


_MODULE = 'pep8'


class Lint (setupext.cmd.Command):
    description = 'lints Python files via `%s`' % _MODULE

    user_options = [
        ('glob', 'g', 'interpret paths as glob patterns'),
        ('include=', 'i', 'paths to lint'),
        ('separator=', 's', 'path separator (comma by default)'),
    ]


    def initialize_options(self):
        self.glob = False
        self.include = None
        self.separator = ','


    def finalize_options(self):
        if self.include is None:
            self.include = []
        else:
            paths = self.include.split(self.separator)

            if self.glob:
                paths = list(itertools.chain.from_iterable(
                    map(glob.glob, paths)))

            self.include = paths


    def run(self):
        argv = [_MODULE] + self.include
        command_line = ' '.join(argv)

        if self.dry_run:
            self.announce('skipping "%s" (dry run)' % command_line)
            return

        self.distribution.fetch_build_eggs(_MODULE)
        script = pkg_resources.load_entry_point(_MODULE,
            'console_scripts', _MODULE)

        sys_argv = sys.argv[:]

        try:
            sys.argv = argv
            self.announce('running "%s"' % command_line)
            script()
        finally:
            sys.argv[:] = sys_argv
