# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division

# External:
import pkg_resources
import setuptools


_MODULE = 'sphinx'
_BUILD_CMD = 'sphinx-build'


class BuildDocs (setuptools.Command, object):
    description = 'builds documentation via `%s`' % _BUILD_CMD

    user_options = [
        ('build-dir=', 'b', 'build directory'),
        ('requirements=', 'r', 'documentation build requirements file'),
        ('source-dir=', 's', 'source directory'),
    ]


    def finalize_options(self):
        if not self.dry_run:
            if self.requirements is not None:
                with open(self.requirements) as reqs:
                    for req in reqs:
                        req = req.strip()

                        if not req.startswith('#'):
                            self.distribution.fetch_build_eggs(req)

            self.distribution.fetch_build_eggs(_MODULE)


    def initialize_options(self):
        self.build_dir = '_docs'
        self.requirements = None
        self.source_dir = 'docs'


    def run(self):
        argv = [_BUILD_CMD, self.source_dir, self.build_dir]
        command_line = ' '.join(argv)

        if self.dry_run:
            self.announce('skipping "%s" (dry run)' % command_line)
            return

        script = pkg_resources.load_entry_point(_MODULE,
            'console_scripts', _BUILD_CMD)

        self.announce('running "%s"' % command_line)
        script(argv = argv)
