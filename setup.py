#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import ast
import codecs
import collections
import imp
import os.path
import re
import sys

# External:
import setuptools


Package = collections.namedtuple('Package', [
    'name', 'version', 'author', 'email', 'docstring', 'readme', 'copyright'])


def get_package():
    name = 'argf'
    docstring = version = None
    module = imp.find_module(name)[0]

    # Avoid having to import the module.
    with module:
        for node in ast.walk(ast.parse(module.read())):
            if isinstance(node, ast.Module):
                docstring = ast.get_docstring(node)
            elif isinstance(node, ast.Assign):
                if any(target.id == '__version__' for target in node.targets):
                    version = ast.literal_eval(node.value)

            if None not in (docstring, version):
                break

    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    license_file = os.path.join(docs_dir, 'LICENSE.txt')
    readme_file = os.path.join(docs_dir, 'README.rst')

    with codecs.open(license_file, encoding = 'UTF-8') as license:
        copyright_line = license.readline()

    [(author, email)] = re.findall(', (.+) <([^<>]+)>$', copyright_line)
    [copyright] = re.findall(r'\(c\) (.+) <', copyright_line)

    return Package(
        name = name,
        version = '.'.join(map(unicode, version)),
        author = author,
        email = email,
        docstring = docstring,
        readme = readme_file,
        copyright = copyright)


if __name__ == '__main__':
    package = get_package()
    is_pre_py27 = sys.version_info < (2, 7)

    with codecs.open(package.readme, encoding = 'UTF-8') as readme:
        long_description = readme.read()

    setuptools.setup(
        name = package.name,
        version = package.version,
        py_modules = [package.name],

        author = package.author,
        author_email = package.email,
        url = 'http://pypi.python.org/pypi/...',
        description = package.docstring.strip().splitlines()[0],
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
