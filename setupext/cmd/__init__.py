# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import abc

# External:
import setuptools


class _CommandMeta (abc.ABCMeta):
    @classmethod
    def normalize_options(mcs, options):
        # Some versions require byte strings.
        if bytes == str:
            return [tuple(map(str, o[:2])) + o[2:] for o in options]
        else:
            return options


    def __new__(mcs, name, bases, attributes):
        user_options = attributes.get('user_options')

        if user_options is not None:
            attributes['user_options'] = mcs.normalize_options(user_options)

        return super(_CommandMeta, mcs).__new__(mcs, name, bases, attributes)


try:
    exec('class _Command (metaclass = _CommandMeta): pass')
except SyntaxError:
    class _Command (object):
        __metaclass__ = _CommandMeta


class Command (setuptools.Command, _Command):
    user_options = []


    def finalize_options(self):
        pass


    def initialize_options(self):
        pass


    @abc.abstractmethod
    def run(self):
        raise NotImplementedError()
