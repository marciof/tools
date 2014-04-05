# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import distutils.cmd

# Internal:
import setupext


requires = []


class Pep8 (distutils.cmd.Command, object):
    description = 'lints via `pep8`'
    user_options = [(b'config=', b'c', 'path to configuration file')]


    def initialize_options(self):
        self.config = None


    def finalize_options(self):
        pass


    def run(self):
        if self.config is not None:
            options = ['--config=' + self.config]
        else:
            options = []

        self.spawn(['pep8'] + options + setupext.globr('*.py'))
