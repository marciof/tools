# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals


env = Environment(
    tools = ['default', 'find', 'pep8', 'pylint', 'pyunit', 'virtualenv'])

src = env.Find('sources')

env.Alias('verify', [
    env.Alias('check', [
        env.Pep8(root = src, config = env.Find('pep8.ini')),
        env.Pylint(root = src, config = env.Find('pylint.ini')),
    ]),
    env.Alias('test', env.PyUnit(root = src))
])

env.Default('verify')
