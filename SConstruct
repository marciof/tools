# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


env = Environment(tools = [
    'default',
    'find',
    'line_profiler_py',
    'pep8',
    'profile_py',
    'python',
    'sphinx',
    'unittest_py',
])

env.AppendENVPath('PYTHONPATH', env.Dir('#'))
tests_path = env.Find('tests')

check_targets = [
    env.Pep8(config = env.Find('pep8.ini')),

    env.PyUnitCoverage('test-coverage',
        sources = ['argf'],
        measure_branch = True,
        html_report = (None if os.environ.get('CI') == 'true' else '_coverage'),
        min_coverage = 100,
        root = tests_path)
]

env.PyUnit('test', root = tests_path)
env.Alias('check', check_targets)

env.Profile('profile-import',
    source = env.Find('argf.py'),
    callers = False)

env.Profile('profile-run',
    source = env.Find('grep.py'))

env.KernProf('profile-line',
    source = env.Find('test_unit.py'))

env.Sphinx('docs',
    source = env.Find('docs'),
    output = '_docs')
