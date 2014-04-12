# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import distutils.errors

# External:
import pkg_resources

# Internal:
import setupext.cmd


_MODULE = 'coverage'


class Measure (setupext.cmd.Command):
    description = 'measure code coverage via `%s`' % _MODULE

    user_options = [
        ('branch', 'b', 'pass the `--branch` command line option'),
        ('input=', 'i', 'Python file to execute'),
        ('module', 'm', 'pass the `--module` command line option'),
    ]


    def initialize_options(self):
        self.branch = False
        self.input = None
        self.module = False


    def finalize_options(self):
        if self.input is None:
            raise distutils.errors.DistutilsOptionError('no input specified')


    def run(self):
        argv = ['run']

        if self.branch:
            argv.append('--branch')

        if self.module:
            argv.append('--module')

        argv.append(self.input)
        command_line = ' '.join([_MODULE] + argv)

        if self.dry_run:
            self.announce('skipping "%s" (dry run)' % command_line)
        else:
            self.distribution.fetch_build_eggs(_MODULE)
            script = pkg_resources.load_entry_point(_MODULE,
                'console_scripts', _MODULE)

            self.announce('running "%s"' % command_line)
            script(argv)
