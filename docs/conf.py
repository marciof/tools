# -*- coding: UTF-8 -*-


"""
Sphinx configuration.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import codecs
import os
import os.path
import sys


# Read The Docs doesn't use SCons, which would set up the environment otherwise,
# so help it find the main module.
root = os.path.join(os.path.dirname(__file__), os.path.pardir)

# (For Sphinx configuration.)
sys.path.append(root)

# (For the `program-output` directive.)
if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] += os.pathsep + root
else:
    os.environ['PYTHONPATH'] = root


# Internal:
import argf


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.programoutput',
]

project = argf.__name__
master_doc = 'index'
exclude_patterns = ['README.*']

with codecs.open('LICENSE.txt', encoding = 'UTF-8') as license_file:
    copyright = license_file.readline().replace('Copyright (c)', '').strip()

version = '.'.join(map(str, argf.__version__))
release = version

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'six': ('http://pythonhosted.org/six/', None),
}
