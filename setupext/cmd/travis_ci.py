# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import pipes
import shlex

# Internal:
import setupext.cmd


requires = []

try:
    _quote_argument = pipes.quote
except AttributeError:
    _quote_argument = shlex.quote


class Lint (setupext.cmd.Command):
    description = 'lints Travis CI config via `Travis::Yaml`'


    def run(self):
        self.spawn(list(map(_quote_argument, [
            'ruby',
            '-r',
            'travis/yaml',
            '-e',
            'Travis::Yaml.parse!(File.read(".travis.yml"))',
        ])))
