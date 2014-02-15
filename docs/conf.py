# -*- coding: UTF-8 -*-


"""
Sphinx configuration.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import codecs
import os.path
import sys

root_dir = os.path.pardir
sys.path.append(root_dir)

# Internal:
import argf


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
]

project = argf.__name__
master_doc = 'index'
license_path = os.path.join(root_dir, 'LICENSE.txt')

with codecs.open(license_path, encoding = 'UTF-8') as license:
    copyright = license.readline().replace('Copyright (c)', '').strip()

version = '.'.join(map(str, argf.__version__))
release = version

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'six': ('http://pythonhosted.org/six/', None),
}
