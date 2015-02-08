# -*- coding: UTF-8 -*-


"""
Sphinx configuration.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import os.path
import sys


project = 'show'
copyright = 'Márcio Moniz Bandim Faustino'
version = '0.1'

extensions = ['sphinx.ext.' + e for e in ('autodoc', 'coverage', 'viewcode')]
master_doc = 'documentation'
html_show_sphinx = False

sys.path.insert(0, os.path.abspath(os.path.pardir))
