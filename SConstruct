# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


env = Environment(tools = [
    'default',
    'find',
    'line_profiler_py',
    'profile_py',
    'python',
    'unittest_py',
])

env.AppendENVPath('PYTHONPATH', env.Dir('#'))
tests_path = env.Find('tests')

env.PyUnit('test', root = tests_path)

env.Alias('check', env.PyUnitCoverage('test-coverage',
    sources = ['argf'],
    measure_branch = True,
    html_report = (None if os.environ.get('CI') == 'true' else '_coverage'),
    min_coverage = 100,
    root = tests_path))

env.Profile('profile-import',
    source = env.Find('argf.py'),
    callers = False)

env.Profile('profile-run',
    source = env.Find('grep.py'))

env.KernProf('profile-line',
    source = env.Find('test_unit.py'))
