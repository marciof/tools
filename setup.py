#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import ast
import codecs
import imp
import os.path
import re
import sys

# External:
import setuptools

# Internal:
import coverage_cmd
import pep8_cmd
import travis_ci_cmd


def _parse_distribution():
    (name, docstring, version) = _parse_module('argf')
    docs_path = os.path.join(os.path.dirname(__file__), 'docs')
    doc_reqs_path = os.path.join(docs_path, 'requirements.txt')
    license_path = os.path.join(docs_path, 'LICENSE.txt')

    with codecs.open(license_path, encoding = 'UTF-8') as license_file:
        copyright_line = license_file.readline()

    with codecs.open(doc_reqs_path, encoding = 'UTF-8') as doc_reqs_file:
        doc_reqs = [l.strip() for l in doc_reqs_file if not l.startswith('#')]

    [(author, email)] = re.findall(', (.+) <([^<>]+)>$', copyright_line)
    [copyright] = re.findall(r'\(c\) (.+) <', copyright_line)

    return (
        name,
        '%d.%d.%d' % version,
        author,
        email,
        docstring,
        doc_reqs,
        os.path.join(docs_path, 'README.rst'),
        copyright)


def _parse_module(name):
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
                return (name, docstring, version)

    raise Exception('failed to extract module information: ' + name)


(name, version, author, email, docstring, doc_reqs, readme, copyright) \
    = _parse_distribution()


if __name__ == '__main__':
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
        name = name,
        version = version,
        py_modules = [name],
        author = author,
        author_email = email,
        url = 'http://pypi.python.org/pypi/' + name,
        description = docstring.strip().splitlines()[0],
        long_description = codecs.open(readme, encoding = 'UTF-8').read(),
        license = 'MIT',
        platforms = 'any',

        test_suite = 'tests',
        tests_require = 'unittest2' if is_pre_py27 else [],
        setup_requires = doc_reqs,

        install_requires = [
            name if version is None else '%s%s' % (name, version)
            for name, version in requirements.items()],

        requires = [
            name if version is None else '%s(%s)' % (name, version)
            for name, version in requirements.items()],

        cmdclass = {
            'coverage': coverage_cmd.Measure,
            'coverage_report': coverage_cmd.Report,
            'lint': pep8_cmd.Lint,
            'travis_lint': travis_ci_cmd.Lint,
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
