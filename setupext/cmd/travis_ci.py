# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import distutils.cmd
import distutils.errors
import shutil


requires = ['shutilwhich']


class Lint (distutils.cmd.Command, object):
    description = 'lints Travis CI config via `Travis::Yaml` or `travis-lint`'
    user_options = []


    def finalize_options(self):
        pass


    def initialize_options(self):
        pass


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
