# -*- coding: UTF-8 -*-

# TODO: Convert to a `setuptools` plug-in like `SetupDocs`.


# Standard:
from __future__ import absolute_import, division
import distutils.errors

# External:
import pkg_resources
import setuptools


_MODULE = 'coverage'


class Measure (setuptools.Command):
    description = 'measure code coverage via `%s`' % _MODULE

    user_options = [
        ('args=', 'a', 'arguments list'),
        ('branch', 'b', 'pass the `--branch` command line option'),
        ('input=', 'i', 'path to Python file to execute'),
        ('module', 'm', 'pass the `--module` command line option'),
        ('separator=', 'p', 'argument separator (blank space by default)'),
        ('source=', 's', 'pass the `--source` command line option'),
        ('test-requires', 't', 'require test dependencies'),
    ]


    def finalize_options(self):
        if self.input is None:
            raise distutils.errors.DistutilsOptionError('no input specified')

        if self.args is None:
            self.args = []
        else:
            self.args = self.args.split(self.separator)

        if not self.dry_run:
            self.distribution.fetch_build_eggs(_MODULE)

            if self.distribution.install_requires:
                self.distribution.fetch_build_eggs(
                    self.distribution.install_requires)

            if self.test_requires and self.distribution.tests_require:
                self.distribution.fetch_build_eggs(
                    self.distribution.tests_require)


    def initialize_options(self):
        self.args = None
        self.branch = False
        self.input = None
        self.module = False
        self.separator = ' '
        self.source = None
        self.test_requires = False


    def run(self):
        argv = ['run']

        if self.branch:
            argv.append('--branch')

        if self.module:
            argv.append('--module')

        if self.source is not None:
            argv.extend(['--source', self.source])

        argv.append(self.input)
        argv.extend(self.args)
        command_line = ' '.join([_MODULE] + argv)

        if self.dry_run:
            self.announce('skipping "%s" (dry run)' % command_line)
        else:
            script = pkg_resources.load_entry_point(_MODULE,
                'console_scripts', _MODULE)

            self.announce('running "%s"' % command_line)
            script(argv)


class Report (setuptools.Command):
    description = 'report code coverage via `%s`' % _MODULE

    user_options = [
        ('fail-under=', 'f', 'pass the `--fail-under` command line option'),
        ('path=', 'p', 'path where to save an HTML report'),
    ]


    def finalize_options(self):
        if not self.dry_run:
            self.distribution.fetch_build_eggs(_MODULE)


    def initialize_options(self):
        self.fail_under = 0
        self.path = None


    def run(self):
        argv = ['html', '--fail-under', self.fail_under]

        if self.path is not None:
            argv.extend(['-d', self.path])

        command_line = ' '.join([_MODULE] + argv)

        if self.dry_run:
            self.announce('skipping "%s" (dry run)' % command_line)
        else:
            script = pkg_resources.load_entry_point(_MODULE,
                'console_scripts', _MODULE)

            self.announce('running "%s"' % command_line)
            script(argv)
