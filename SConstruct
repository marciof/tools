# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


env = Environment(tools = [
    'default', 'find', 'pep8', 'pyprofile', 'python', 'pyunit', 'sphinx'])

tests_path = env.Find('tests')
in_continuous_integration = (os.environ.get('CI') == 'true')

check_targets = [
    env.Pep8(config = env.Find('pep8.ini')),

    env.PyUnitCoverage('test-coverage',
        sources = ['argf'],
        measure_branch = True,
        html_report = (None if in_continuous_integration else '_coverage'),
        min_coverage = 100,
        root = tests_path)
]

if not in_continuous_integration:
    env.Tool('travis-lint')
    check_targets.insert(0, env.TravisLint())

env.PyUnit('test', root = tests_path)
env.Alias('check', check_targets)

env.Alias('profile', [
    env.Profile('profile-import',
        source = env.Find('argf.py'),
        callers = False),

    env.Profile('profile-run',
        source = env.Find('grep.py')),
])

env.Sphinx('docs', source = env.Find('docs'))
