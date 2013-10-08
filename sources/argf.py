# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import inspect
import re
import xml.etree.ElementTree

# External:
import argparse
import docutils.core


class Error (Exception):
    pass


class Argument (object):
    _NO_DEFAULT_VALUE = object()


    def __init__(self, name):
        self.name = name
        self.data_type = None
        self.description = None
        self.short_name = None
        self._default_value = self._NO_DEFAULT_VALUE


    def __eq__(self, other):
        return hash(self) == hash(other)


    def __hash__(self):
        return hash(self.name)


    @property
    def default_value(self):
        if not self.has_default_value:
            raise Error('Argument has no default value.')
        else:
            return self._default_value


    @default_value.setter
    def default_value(self, value):
        self._default_value = value


    @property
    def has_default_value(self):
        return self._default_value is not self._NO_DEFAULT_VALUE


    def guess_data_type(self):
        if self.data_type is not None:
            return self.data_type

        if self.has_default_value:
            return type(self.default_value)

        return str


def extract_arguments(function, reserved_names):
    arg_spec = inspect.getargspec(function)
    reserved_names = set(reserved_names)

    if (arg_spec.varargs is not None) or (arg_spec.keywords is not None):
        raise Error('Varargs and kwargs are not supported.')

    nr_kwargs = 0 if arg_spec.defaults is None else len(arg_spec.defaults)
    kwargs_offset = len(arg_spec.args) - nr_kwargs
    arguments = []

    for name, arg_i in zip(arg_spec.args, range(len(arg_spec.args))):
        if name in reserved_names:
            raise Error('Argument name is reserved: ' + name)

        reserved_names.add(name)
        argument = Argument(name)

        for c in name:
            if c not in reserved_names:
                reserved_names.add(c)
                argument.short_name = c
                break

        kwarg_i = arg_i - kwargs_offset
        has_default = (0 <= kwarg_i < nr_kwargs)

        if has_default:
            argument.default_value = arg_spec.defaults[kwarg_i]

        arguments.append(argument)

    return arguments


def get_type_by_name(name):
    try:
        return __builtins__[name]
    except KeyError:
        raise Error('No such data type: ' + name)


# TODO: Leverage Sphinx to parse docstrings in the Python domain.
def parse_docstring(function, arguments):
    docstring = inspect.getdoc(function)

    if docstring is None:
        return None

    arguments = dict((param.name, param) for param in arguments)
    has_description = set()
    has_data_type = set()

    docstring = xml.etree.ElementTree.fromstring(
        docutils.core.publish_doctree(docstring).asdom().toxml())

    for fields in docstring.findall('field_list'):
        for field in fields.findall('field'):
            field_name = field.findtext('field_name')
            directive = re.match(r'^(\w+)\s+([^\s]*)$', field_name)

            if directive is None:
                raise Error('Invalid field: ' + field_name)

            (kind, name) = directive.groups()
            argument = arguments.get(name)

            if argument is None:
                raise Error('Unknown parameter: ' + name)

            field_body = field.findtext('field_body/paragraph')

            if kind == 'param':
                if argument in has_description:
                    raise Error('Ambiguous parameter description: ' + name)

                argument.description = field_body
                has_description.add(argument)
            elif kind == 'type':
                if argument in has_data_type:
                    raise Error('Ambiguous parameter data type: ' + name)

                argument.data_type = get_type_by_name(field_body)
                has_data_type.add(argument)
            else:
                raise Error('Unknown field: ' + field_name)

    return docstring.findtext('paragraph')


# TODO: Allow user defined arg parser (and update reserved names).
def start(main, args = None):
    arg_parser = argparse.ArgumentParser(
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    if arg_parser.add_help:
        reserved_names = set(['h', 'help'])
    else:
        reserved_names = set()

    arguments = extract_arguments(main, reserved_names)
    arg_parser.description = parse_docstring(main, arguments)

    for argument in arguments:
        names = []
        options = {}

        if argument.description is not None:
            options['help'] = argument.description

        if argument.has_default_value:
            if argument.short_name is not None:
                names.append('-' + argument.short_name)

            names.append('--' + argument.name)
            options['default'] = argument.default_value
            data_type = argument.guess_data_type()

            if issubclass(data_type, bool):
                options['const'] = not argument.default_value
                options['action'] = 'store_const'
            else:
                options['type'] = data_type
        else:
            names.append(argument.name)

        arg_parser.add_argument(*names, **options)

    return main(**arg_parser.parse_args(args = args).__dict__)
