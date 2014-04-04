# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import abc

# External:
import setuptools


class CommandMeta (abc.ABCMeta):
    @classmethod
    def normalize_options(mcs, options):
        return [tuple(map(str, option[:2])) + option[2:] for option in options]


    def __new__(mcs, name, bases, attributes):
        user_options = attributes.get('user_options')

        if user_options is not None:
            attributes['user_options'] = mcs.normalize_options(user_options)

        return super(CommandMeta, mcs).__new__(mcs, name, bases, attributes)


class Command (setuptools.Command, object):
    __metaclass__ = CommandMeta
    user_options = []


    def finalize_options(self):
        pass


    def initialize_options(self):
        pass


    @abc.abstractmethod
    def run(self):
        raise NotImplementedError()
