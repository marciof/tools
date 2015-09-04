# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division
import re
import subprocess
import sys

# External:
import pkg_resources
import setuptools


_MODULE = 'sphinx'
_BUILD_CMD = 'sphinx-build'


try:
    _check_output = subprocess.check_output
except AttributeError:
    def _check_output(command):
        process = subprocess.Popen(command,
            stderr = subprocess.PIPE,
            stdout = subprocess.PIPE)

        output = process.communicate()[0]
        exit_code = process.poll()

        if exit_code:
            raise subprocess.CalledProcessError(exit_code, command)

        return output


class BuildDocs (setuptools.Command, object):
    description = 'build documentation via `%s`' % _BUILD_CMD

    user_options = [
        ('build-dir=', 'b', 'build directory'),
        ('requirements=', 'r', 'documentation build requirements.txt file'),
        ('setup-requirements', 'i', '`setup.py --requires` requirements list'),
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

            if self.setup_requirements:
                reqs = _check_output(
                    [sys.executable, sys.argv[0], '--requires'])

                for req in reqs.splitlines():
                    self.distribution.fetch_build_eggs(
                        re.sub(r'\(([^()]+)\)$', r'\1', req))

            # Install at the end to give a chance for a different version to
            # be specified.
            self.distribution.fetch_build_eggs(_MODULE)


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
