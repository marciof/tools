# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import distutils.errors
import shutil

# Internal:
import setupext.cmd


requires = ['shutilwhich']


class Lint (setupext.cmd.Command):
    description = 'lints via `Travis::Yaml` or `travis-lint`'


    def run(self):
        try:
            self.spawn([
                'ruby',
                '-r',
                'travis/yaml',
                '-e',
                '''"Travis::Yaml.parse!(File.read('.travis.yml'))"''',
            ])
            return
        except distutils.errors.DistutilsExecError:
            pass

        for module in requires:
            __import__(module)

        travis_lint = shutil.which('travis-lint')

        if travis_lint is not None:
            self.spawn([travis_lint])
            return

        raise distutils.errors.DistutilsError(
            'neither `Travis::Yaml` nor `travis-lint` found')
