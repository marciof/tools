#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import ast
import codecs
import imp
import os.path
import sys

# External:
import setuptools


def extract_info():
    """
    :return: module's name, version, and docstring
    :rtype: tuple<unicode, unicode, unicode>
    """

    name = 'argf'
    docstring = version = None
    (module, path, description) = imp.find_module(name)

    # Avoid having to import the module.
    with module:
        for node in ast.walk(ast.parse(module.read())):
            if isinstance(node, ast.Module):
                docstring = ast.get_docstring(node)
            elif isinstance(node, ast.Assign):
                if any(target.id == '__version__' for target in node.targets):
                    version = ast.literal_eval(node.value)

            if None not in (docstring, version):
                return (name, '.'.join(map(unicode, version)), docstring)


if __name__ == '__main__':
    (name, version, docstring) = extract_info()

    docs_path = 'docs'
    readme_file = os.path.join(docs_path, 'README.rst')
    license_file = os.path.join(docs_path, 'LICENSE.txt')
    is_pre_py27 = sys.version_info < (2, 7)

    with codecs.open(readme_file, encoding = 'UTF-8') as readme:
        long_description = readme.read()

    with codecs.open(license_file, encoding = 'UTF-8') as license:
        author = license.readline().split(',')[-1].strip()

    setuptools.setup(
        name = name,
        version = version,
        py_modules = [name],

        author = author,
        description = docstring.strip().splitlines()[0],
        long_description = long_description,
        license = 'MIT',

        test_suite = 'tests',
        tests_require = 'unittest2' if is_pre_py27 else [],

        install_requires = ['docutils', 'six']
            # Earlier versions don't take `prefix_chars` into account when
            # creating the help option.
            + ['argparse>=1.2.1'] if is_pre_py27 else [],

        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ])
