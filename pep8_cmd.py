# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division
import glob
import itertools
import sys

# External:
import pkg_resources
import setuptools


_MODULE = 'pep8'


class Lint (setuptools.Command, object):
    description = 'lints Python files via `%s`' % _MODULE

    user_options = [
        ('glob', 'g', 'interpret paths as glob patterns'),
        ('include=', 'i', 'paths to lint'),
        ('separator=', 's', 'path separator (comma by default)'),
    ]


    def finalize_options(self):
        if self.include is None:
            self.include = []
        else:
            paths = self.include.split(self.separator)

            if self.glob:
                paths = list(itertools.chain.from_iterable(
                    map(glob.glob, paths)))

            self.include = paths

        if not self.dry_run:
            self.distribution.fetch_build_eggs(_MODULE)


    def initialize_options(self):
        self.glob = False
        self.include = None
        self.separator = ','


    def run(self):
        argv = [_MODULE] + self.include
        command_line = ' '.join(argv)

        if self.dry_run:
            self.announce('skipping "%s" (dry run)' % command_line)
            return

        script = pkg_resources.load_entry_point(_MODULE,
            'console_scripts', _MODULE)
        sys_argv = sys.argv[:]

        try:
            sys.argv = argv
            self.announce('running "%s"' % command_line)
            script()
        finally:
            sys.argv[:] = sys_argv
