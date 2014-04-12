# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import distutils.errors
import distutils.log

# Internal:
import setupext.cmd


class Measure (setupext.cmd.Command):
    description = 'measure code coverage via `coverage`'

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
            raise distutils.errors.DistutilsOptionError('no script specified')


    def run(self):
        self.distribution.fetch_build_eggs('coverage')

        # External:
        import coverage

        argv = ['run']

        if self.branch:
            argv.append('--branch')

        if self.module:
            argv.append('--module')

        argv.append(self.input)
        command_line = ' '.join([coverage.__name__] + argv)

        if self.dry_run:
            self.announce('skipping "%s" (dry run)' % command_line)
        else:
            self.announce('running "%s"' % command_line)
            coverage.main(argv)
