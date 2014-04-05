# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import shutil
import subprocess

# Internal:
import setupext.cmd


requires = ['shutilwhich'] if not hasattr(shutil, 'which') else []


class Lint (setupext.cmd.Command):
    description = 'lints the Travis CI configuration file'


    def run(self):
        for module in requires:
            __import__(module)

        ruby = shutil.which('ruby')

        if ruby is not None:
            subprocess.call([
                ruby,
                '-r',
                'travis/yaml',
                '-e',
                'Travis::Yaml.parse!(File.read(".travis.yml"))',
            ])
            return

        travis_lint = shutil.which('travis-lint')

        if travis_lint is not None:
            subprocess.call([travis_lint])
            return

        self.warn('neither `ruby` nor `travis-lint` found')
