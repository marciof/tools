# -*- coding: UTF-8 -*-


"""
Sphinx configuration.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os
import os.path
import sys


# Read The Docs doesn't use SCons which would set up the environment otherwise.
root = os.path.join(os.path.dirname(__file__), os.path.pardir)

# Help Sphinx find the setup module.
sys.path.append(root)

# Help the `program-output` directive find the main module.
if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] += os.pathsep + root
else:
    os.environ['PYTHONPATH'] = root


# Internal:
import setup


project = setup.name
version = setup.version
release = setup.version
master_doc = 'index'
exclude_patterns = ['README.*']
copyright = setup.copyright

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.programoutput',
]

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'six': ('http://pythonhosted.org/six/', None),
}
