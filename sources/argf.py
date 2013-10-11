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


class AmbiguousDocDescription (Error):
    def __str__(self):
        return 'custom arg parser instance already defines a description'


class AmbiguousDocParamDesc (Error):
    def __str__(self):
        return 'multiple descriptions for same parameter in docstring: %s' \
            % self.args


class AmbiguousDocParamType (Error):
    def __str__(self):
        return 'multiple types for same parameter in docstring: %s' % self.args


class DynamicArgs (Error):
    def __str__(self):
        return 'varargs and kwargs are not supported'


class IncompatibleParamDocTypes (Error):
    def __str__(self):
        return 'default value and docstring types are not compatible: %s' \
            % self.args


class ReservedParamName (Error):
    def __str__(self):
        return 'parameter name is reserved: %s' % self.args


class UnknownDocParam (Error):
    def __str__(self):
        return 'unknown parameter in docstring: %s' % self.args


class UnknownDocType (Error):
    def __str__(self):
        return 'unknown parameter type in docstring: %s' % self.args


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
            raise Error('argument has no default value')
        else:
            return self._default_value


    @default_value.setter
    def default_value(self, value):
        self._default_value = value


    @property
    def has_default_value(self):
        return self._default_value is not self._NO_DEFAULT_VALUE


    def guess_data_type(self):
        data_type = self.data_type

        if self.has_default_value and (self.default_value is not None):
            inferred_data_type = type(self.default_value)

            if data_type is None:
                data_type = inferred_data_type
            elif not issubclass(inferred_data_type, data_type):
                raise IncompatibleParamDocTypes(self.name)
        elif data_type is None:
            data_type = str

        return data_type


def add_options(arg_parser, arguments):
    for argument in arguments:
        names = []
        options = {}

        if argument.description is not None:
            options['help'] = argument.description

        if argument.has_default_value:
            if argument.short_name is not None:
                names.append(arg_parser.prefix_chars + argument.short_name)

            data_type = argument.guess_data_type()
            names.append((2 * arg_parser.prefix_chars) + argument.name)
            options['default'] = argument.default_value

            if issubclass(data_type, bool):
                options['const'] = not argument.default_value
                options['action'] = 'store_const'
            else:
                options['type'] = data_type
        else:
            names.append(argument.name)

        arg_parser.add_argument(*names, **options)


def extract_arguments(function, reserved_names):
    arg_spec = inspect.getargspec(function)
    reserved_names = set(reserved_names)

    if (arg_spec.varargs is not None) or (arg_spec.keywords is not None):
        raise DynamicArgs()

    nr_kwargs = 0 if arg_spec.defaults is None else len(arg_spec.defaults)
    kwargs_offset = len(arg_spec.args) - nr_kwargs
    arguments = []

    for name, arg_i in zip(arg_spec.args, range(len(arg_spec.args))):
        kwarg_i = arg_i - kwargs_offset
        is_optional = (0 <= kwarg_i < nr_kwargs)

        if is_optional and (name in reserved_names):
            raise ReservedParamName(name)

        reserved_names.add(name)
        argument = Argument(name)

        for char in name:
            if char not in reserved_names:
                reserved_names.add(char)
                argument.short_name = char
                break

        if is_optional:
            argument.default_value = arg_spec.defaults[kwarg_i]

        arguments.append(argument)

    return arguments


def get_type_by_name(name):
    try:
        return __builtins__[name]
    except KeyError:
        raise UnknownDocType(name)


def parse_docstring(function, arguments):
    docstring = inspect.getdoc(function)

    if docstring is None:
        return None

    arguments = dict((param.name, param) for param in arguments)
    has_description = set()
    has_data_type = set()

    docstring = xml.etree.ElementTree.fromstring(
        docutils.core.publish_doctree(docstring).asdom().toxml())

    for field in docstring.findall('.//field'):
        field_name = field.findtext('field_name')
        directive = re.match(r'^(\w+)\s+([^\s]*)$', field_name)

        if directive is None:
            continue

        (kind, name) = directive.groups()
        argument = arguments.get(name)

        if argument is None:
            raise UnknownDocParam(name)

        field_body = field.findtext('field_body/paragraph')

        if kind == 'param':
            if argument in has_description:
                raise AmbiguousDocParamDesc(name)

            argument.description = field_body
            has_description.add(argument)
        elif kind == 'type':
            if argument in has_data_type:
                raise AmbiguousDocParamType(name)

            argument.data_type = get_type_by_name(field_body)
            has_data_type.add(argument)

    return docstring.findtext('paragraph')


def start(main,
        args = None,
        arg_parser = None,
        soft_errors = True):

    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    if arg_parser.add_help:
        reserved_names = set(['h', 'help'])
    else:
        reserved_names = set()

    try:
        arguments = extract_arguments(main, reserved_names)
        description = parse_docstring(main, arguments)

        if description is not None:
            if arg_parser.description is None:
                arg_parser.description = description
            else:
                raise AmbiguousDocDescription()

        add_options(arg_parser, arguments)
    except Error as error:
        if soft_errors:
            arg_parser.error(error)
        else:
            raise
    else:
        return main(**arg_parser.parse_args(args = args).__dict__)
