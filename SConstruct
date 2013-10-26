# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals


env = Environment(
    tools = ['default', 'find', 'pep8', 'python', 'pyunit', 'travis-lint'])

travis_lint = env.TravisLint()
pep8 = env.Pep8(config = env.Find('pep8.ini'))
test = env.PyUnit('test')

test_coverage = env.PyUnitCoverage('test-coverage',
    sources = ['argf'],
    measure_branch = True)

if env['TRAVIS_CI']:
    env.Alias('check', [pep8, test_coverage])
else:
    env.Alias('check', [travis_lint, pep8, test])
