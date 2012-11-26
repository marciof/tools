# -*- coding: UTF-8 -*-


# Standard:
import os.path, sys


project = u'show'
copyright = u'Márcio Moniz Bandim Faustino'
version = '0.1'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.viewcode']
master_doc = 'Documentation'
html_show_sphinx = False

sys.path.insert(0, os.path.abspath(os.path.pardir))
