# -*- coding: UTF-8 -*-


"""
Sphinx configuration.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import codecs
import os.path
import sys

sys.path.append(os.path.curdir)

# Internal:
import argf


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
]

project = argf.__name__
master_doc = 'doc'

with codecs.open('LICENSE.txt', encoding = 'UTF-8') as license:
    copyright = license.readline().replace('Copyright (c)', '').strip()

version = '.'.join(map(str, argf.__version__))
release = version

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'six': ('http://pythonhosted.org/six/', None),
}
