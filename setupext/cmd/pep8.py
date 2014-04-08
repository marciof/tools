# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import distutils.log
import glob
import itertools
import sys

# Internal:
import setupext.cmd


requires = ['pep8']


class Pep8 (setupext.cmd.Command):
    description = 'lints Python files via `pep8`'

    user_options = [
        ('include=', 'p', 'comma separated glob patterns to lint'),
        ('separator=', 's', 'pattern separator'),
    ]


    def initialize_options(self):
        self.include = None
        self.separator = ','


    def finalize_options(self):
        if self.include is None:
            self.include = []
        else:
            self.include = list(itertools.chain.from_iterable(map(glob.glob,
                self.include.split(self.separator))))


    def run(self):
        (pep8,) = map(__import__, requires)

        # TODO: Use the `pep8` script instead.
        argv = sys.argv

        try:
            sys.argv = ['pep8'] + self.include
            self.announce(' '.join(sys.argv), distutils.log.INFO)
            pep8._main()
        finally:
            sys.argv = argv
