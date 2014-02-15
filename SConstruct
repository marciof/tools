# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os


env = Environment(tools = [
    'default', 'find', 'pep8', 'pyprofile', 'python', 'pyunit', 'sphinx'])

check_targets = [env.Pep8(config = env.Find('pep8.ini'))]

test = env.PyUnit('test',
    root = env.Find('tests'),
    pattern = '*.py')

test_coverage = env.PyUnitCoverage('test-coverage',
    sources = ['argf'],
    measure_branch = True)

if (os.environ.get('TRAVIS') == 'true') and (os.environ.get('CI') == 'true'):
    check_targets.append(test_coverage)
else:
    env.Tool('travis-lint')
    check_targets.insert(0, env.TravisLint())
    check_targets.append(test)

env.Alias('check', check_targets)

env.Alias('profile', [
    env.Profile('profile-import',
        source = env.Find('argf.py'),
        callers = False),

    env.Profile('profile-run',
        source = env.Find('profile_run.py')),
])

env.Sphinx('documentation')
