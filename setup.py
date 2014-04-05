#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import collections
import os.path
import re
import sys

# External:
import setuptools

# Internal:
import setupext
import setupext.cmd.travis_ci


Package = collections.namedtuple('Package', [
    'name', 'version', 'author', 'email', 'docstring', 'readme', 'copyright'])


def get_package():
    (name, docstring, version) = setupext.extract_details('argf')

    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    license_file = os.path.join(docs_dir, 'LICENSE.txt')
    readme_file = os.path.join(docs_dir, 'README.rst')
    copyright_line = setupext.read_text(license_file, lambda f: f.readline())

    [(author, email)] = re.findall(', (.+) <([^<>]+)>$', copyright_line)
    [copyright] = re.findall(r'\(c\) (.+) <', copyright_line)

    return Package(
        name = name,
        version = '%d.%d.%d' % version,
        author = author,
        email = email,
        docstring = docstring,
        readme = readme_file,
        copyright = copyright)


if __name__ == '__main__':
    package = get_package()
    is_pre_py27 = sys.version_info < (2, 7)

    requirements = {
        'docutils': None,
        'six': None,
    }

    if is_pre_py27:
        # Earlier versions don't take `prefix_chars` into account when
        # creating the help option.
        requirements['argparse'] = '>=1.2.1'

    setuptools.setup(
        name = package.name,
        version = package.version,
        py_modules = [package.name],
        test_suite = 'tests',

        author = package.author,
        author_email = package.email,
        url = 'http://pypi.python.org/pypi/' + package.name,
        description = package.docstring.strip().splitlines()[0],
        long_description = setupext.read_text(package.readme),
        license = 'MIT',
        platforms = 'any',

        tests_require = 'unittest2' if is_pre_py27 else [],
        setup_requires = setupext.cmd.travis_ci.requires,
        install_requires = setupext.to_install_requires(requirements),
        requires = setupext.to_requires(requirements),

        cmdclass = {
            'travis_lint': setupext.cmd.travis_ci.Lint,
        },

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
