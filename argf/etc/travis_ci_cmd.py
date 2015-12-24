# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division
import distutils.errors
import pipes
import shlex

# External:
import setuptools


try:
    _quote_shell_arg = pipes.quote
except AttributeError:
    _quote_shell_arg = shlex.quote


class Lint (setuptools.Command, object):
    description = 'lint Travis CI config files via `Travis::Yaml`'
    user_options = []


    def finalize_options(self):
        pass


    def initialize_options(self):
        pass


    def run(self):
        find_ruby_alternatives = [
            self._find_ruby_from_path,
            self._find_ruby_from_winreg,
        ]

        for find_ruby in find_ruby_alternatives:
            try:
                self.spawn([find_ruby()] + list(map(_quote_shell_arg, [
                    '-r',
                    'travis/yaml',
                    '-e',
                    'Travis::Yaml.parse!(File.read(".travis.yml"))',
                ])))
            except distutils.errors.DistutilsPlatformError:
                continue
            else:
                break
        else:
            raise distutils.errors.DistutilsPlatformError(
                'unable to find a Ruby interpreter')


    def _find_ruby_from_path(self):
        import subprocess
        ruby = 'ruby'

        try:
            subprocess.call([ruby, '-e', '1'])
        except OSError as error:
            raise distutils.errors.DistutilsPlatformError(error)
        else:
            return ruby


    def _find_ruby_from_winreg(self):
        try:
            import _winreg as winreg
        except ImportError:
            try:
                import winreg
            except ImportError as error:
                raise distutils.errors.DistutilsPlatformError(error)

        ruby_file_open_cmd = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Classes\RubyFile\shell\open\command',
            0,
            winreg.KEY_QUERY_VALUE)

        ruby = shlex.split(winreg.QueryValue(ruby_file_open_cmd, None))

        if len(ruby) < 1:
            raise distutils.errors.DistutilsPlatformError()
        else:
            return ruby[0]
