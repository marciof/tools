# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import pipes
import shlex

# Internal:
import setupext.cmd


try:
    _quote_shell_arg = pipes.quote
except AttributeError:
    _quote_shell_arg = shlex.quote


class Lint (setupext.cmd.Command):
    description = 'lints Travis CI config via `Travis::Yaml`'


    def run(self):
        self.spawn(list(map(_quote_shell_arg, [
            'ruby',
            '-r',
            'travis/yaml',
            '-e',
            'Travis::Yaml.parse!(File.read(".travis.yml"))',
        ])))
