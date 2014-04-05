# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import ast
import codecs
import glob
import imp
import itertools
import os.path


def extract_details(name):
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


def globr(pattern, root = os.path.curdir):
    """
    :type pattern: unicode
    :param pattern: glob pattern
    :type root: unicode
    :param root: search starting point path
    :rtype: list<unicode>
    :return: matching files
    """

    paths = glob.glob(os.path.join(root, pattern))

    for path, dirs, files in os.walk(root):
        paths.extend(itertools.chain.from_iterable(
            [glob.glob(os.path.join(d, pattern)) for d in dirs]))

    return paths


def read_text(path, read = lambda f: f.read(), encoding = 'UTF-8'):
    with codecs.open(path, encoding = encoding) as f:
        return read(f)


def to_install_requires(requirements):
    return [
        name if version is None else name + version
        for name, version in requirements.items()]


def to_requires(requirements):
    return [
        name if version is None else '%s(%s)' % (name, version)
        for name, version in requirements.items()]
