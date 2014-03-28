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


# Read The Docs doesn't use SCons, which would set up the environment
# otherwise, so help it find the setup module.
root = os.path.join(os.path.dirname(__file__), os.path.pardir)

# (For Sphinx configuration.)
sys.path.append(root)

# (For the `program-output` directive.)
if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] += os.pathsep + root
else:
    os.environ['PYTHONPATH'] = root


# Internal:
from setup import extract_info


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.programoutput',
]

(name, version, docstring) = extract_info()
project = name
release = version
master_doc = 'index'
exclude_patterns = ['README.*']

with codecs.open('LICENSE.txt', encoding = 'UTF-8') as license:
    copyright = license.readline().strip().replace('Copyright (c)', '')

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'six': ('http://pythonhosted.org/six/', None),
}
