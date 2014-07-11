# -*- coding: UTF-8 -*-


"""
Sphinx configuration.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os
import os.path
import sys


# Prepare the environment for Sphinx:
root = os.path.join(os.path.dirname(__file__), os.path.pardir)

# - Help it find the setup module.
sys.path.append(root)

# - Help the `program-output` directive find the main module and dependencies.
if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] += os.pathsep + os.pathsep.join(sys.path)
else:
    os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)


# Internal:
import setup as distribution # Avoid clashing with Sphinx options.


project = distribution.name
version = distribution.version
release = distribution.version
master_doc = 'index'
exclude_patterns = ['CHANGES.*', 'README.*']
copyright = distribution.copyright

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.programoutput',
]

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'six': ('http://pythonhosted.org/six/', None),
}
