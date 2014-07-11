# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division
import subprocess
import sys

# External:
import pkg_resources
import setuptools


_MODULE = 'sphinx'
_BUILD_CMD = 'sphinx-build'


class BuildDocs (setuptools.Command, object):
    description = 'builds documentation via `%s`' % _BUILD_CMD

    user_options = [
        ('build-dir=', 'b', 'build directory'),
        ('requirements=', 'r', 'documentation build requirements.txt file'),
        ('setup-requirements', 'i', '`setup.py --requires` requirements list'),
        ('source-dir=', 's', 'source directory'),
    ]


    def finalize_options(self):
        if not self.dry_run:
            self.distribution.fetch_build_eggs(_MODULE)

            if self.requirements is not None:
                with open(self.requirements) as reqs:
                    for req in reqs:
                        req = req.strip()

                        if not req.startswith('#'):
                            self.distribution.fetch_build_eggs(req)

            if self.setup_requirements:
                reqs = subprocess.check_output(
                    [sys.executable, sys.argv[0], '--requires'])

                for req in reqs.splitlines():
                    self.distribution.fetch_build_eggs(req)


    def initialize_options(self):
        self.build_dir = '_docs'
        self.requirements = None
        self.setup_requirements = False
        self.source_dir = 'docs'


    def run(self):
        argv = [_BUILD_CMD, '-W', self.source_dir, self.build_dir]
        command_line = ' '.join(argv)

        if self.dry_run:
            self.announce('skipping "%s" (dry run)' % command_line)
            return

        script = pkg_resources.load_entry_point(_MODULE,
            'console_scripts', _BUILD_CMD)

        self.announce('running "%s"' % command_line)
        script(argv = argv)
