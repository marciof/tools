# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division
import pipes
import shlex

# External:
import setuptools


try:
    _quote_shell_arg = pipes.quote
except AttributeError:
    _quote_shell_arg = shlex.quote


class Lint (setuptools.Command, object):
    description = 'lints Travis CI config via `Travis::Yaml`'
    user_options = []


    def finalize_options(self):
        pass


    def initialize_options(self):
        pass


    def run(self):
        self.spawn(list(map(_quote_shell_arg, [
            'ruby',
            '-r',
            'travis/yaml',
            '-e',
            'Travis::Yaml.parse!(File.read(".travis.yml"))',
        ])))
