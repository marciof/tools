# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import errno
import subprocess

# Internal:
import setupcmds.base


class Lint (setupcmds.base.Command):
    description = 'executes `travis-lint`'


    def run(self):
        try:
            subprocess.check_call('travis-lint', shell = True)
        except subprocess.CalledProcessError as error:
            raise OSError(errno.EINVAL, error)
