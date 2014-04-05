# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import distutils.cmd


requires = ['pep8', 'glob2']


class Pep8 (distutils.cmd.Command, object):
    description = 'lints Python files via `pep8`'
    user_options = []


    def initialize_options(self):
        pass


    def finalize_options(self):
        pass


    def run(self):
        glob2 = __import__(requires[0])
        self.spawn(['pep8'] + glob2.glob('**/*.py'))
