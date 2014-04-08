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
        ('input=', 'i', 'Python file to execute'),
        ('module', 'm', 'input is a module, instead of a script'),
    ]


    def initialize_options(self):
        self.input = None
        self.module = False


    def finalize_options(self):
        if self.input is None:
            raise distutils.errors.DistutilsOptionError('no script specified')


    def run(self):
        self.distribution.fetch_build_eggs('coverage')

        # External:
        import coverage

        argv = ['run', '--branch']

        if self.module:
            argv.append('--module')

        argv.append(self.input)
        self.announce(' '.join([coverage.__name__] + argv), distutils.log.INFO)
        coverage.main(argv)
