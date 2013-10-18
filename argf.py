# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import inspect
import re
import xml.etree.ElementTree

# External:
import docutils.core
import six
import six.moves


class Error (Exception):
    pass


class AmbiguousParamDesc (Error):
    def __str__(self):
        return 'ambiguous parameter description: %s' % self.args


class AmbiguousParamDataType (Error):
    def __str__(self):
        return 'ambiguous parameter data type: %s' % self.args


class DynamicArgs (Error):
    def __str__(self):
        return 'varargs and kwargs are not supported'


class IncompatibleParamDataTypes (Error):
    def __str__(self):
        return 'default value and docstring types are not compatible: %s' \
            % self.args


class ParamDataTypeImportError (Error):
    def __str__(self):
        return 'failed to import parameter data type: %s: %s' % self.args


class UnknownParams (Error):
    def __str__(self):
        (names,) = self.args
        return 'unknown parameter(s): %s' % ', '.join(sorted(names))


class UnknownParamDataType (Error):
    def __str__(self):
        return 'unknown parameter data type: %s' % self.args


class Argument (object):
    def __init__(self, name, data_type = six.text_type, description = None):
        self.name = name
        self.data_type = data_type
        self.description = description


    def validate(self):
        pass


class OptionArgument (Argument):
    def __init__(self, name, default_value, **kwargs):
        Argument.__init__(self, name, **kwargs)
        self.default_value = default_value


    def validate(self):
        value = self.default_value

        if (value is not None) and not isinstance(value, self.data_type):
            raise IncompatibleParamDataTypes(self.name)


def extract_arguments(function):
    """
    :type function: types.FunctionType
    :rtype: tuple<None | six.text_type, list<Argument>>
    :raise UnknownParams:
    """

    (main_desc, data_types, descriptions) = extract_documentation(function)
    args = []

    for param in extract_parameters(function):
        if isinstance(param, tuple):
            (name, default_value) = param
            arg = OptionArgument(name = name, default_value = default_value)
        else:
            (name,) = param
            arg = Argument(name = name)

        if arg.name in data_types:
            arg.data_type = data_types.pop(arg.name)

        if arg.name in descriptions:
            arg.description = descriptions.pop(arg.name)

        arg.validate()
        args.append(arg)

    if (len(data_types) > 0) or (len(descriptions) > 0):
        raise UnknownParams(set(data_types.keys() + descriptions.keys()))

    return (main_desc, args)


# TODO: Leverage Sphinx for parsing, but provide a fallback.
def extract_documentation(function):
    """
    :type function: types.FunctionType
    :rtype: tuple<
        None | six.text_type,
        dict<six.text_type, six.class_types>,
        dict<six.text_type, six.text_type>>
    :raise AmbiguousParamDesc:
    :raise AmbiguousParamType:
    """

    data_types = {}
    descriptions = {}
    docstring = inspect.getdoc(function) or ''

    doc = xml.etree.ElementTree.fromstring(
        docutils.core.publish_doctree(docstring).asdom().toxml())

    for field in doc.findall('.//field'):
        field_name = field.findtext('field_name')
        directive = re.match(r'^(\w+)\s+([^\s]*)$', field_name)

        if directive is None:
            continue

        (kind, name) = directive.groups()
        field_body = field.findtext('field_body/paragraph')

        if kind == 'param':
            if name in descriptions:
                raise AmbiguousParamDesc(name)
            else:
                descriptions[name] = field_body
        elif kind == 'type':
            if name in data_types:
                raise AmbiguousParamDataType(name)
            else:
                data_types[name] = load_data_type(field_body)

    return (doc.findtext('paragraph'), data_types, descriptions)


def extract_parameters(function):
    """
    :type function: types.FunctionType
    :rtype: list<six.text_type | tuple<six.text_type, object>>
    :raise DynamicArgs:
    """

    arg_spec = inspect.getargspec(function)

    if (arg_spec.varargs is not None) or (arg_spec.keywords is not None):
        raise DynamicArgs()

    nr_kwargs = 0 if arg_spec.defaults is None else len(arg_spec.defaults)
    kwargs_offset = len(arg_spec.args) - nr_kwargs
    params = []

    for name, arg_i in zip(arg_spec.args, range(len(arg_spec.args))):
        kwarg_i = arg_i - kwargs_offset
        is_keyword = (0 <= kwarg_i < nr_kwargs)

        if is_keyword:
            params.append((name, arg_spec.defaults[kwarg_i]))
        else:
            params.append(name)

    return params


def load_data_type(name):
    """
    :type name: six.text_type
    :rtype: six.class_types
    """

    if '.' not in name:
        (module, type_name) = (six.moves.builtins, name)
    else:
        (module, type_name) = name.rsplit('.', 1)

        try:
            module = __import__(module)
        except ImportError as error:
            raise ParamDataTypeImportError(name, error)

    try:
        return getattr(module, type_name)
    except AttributeError:
        raise UnknownParamDataType(name)


'''
"""
Declarative command line arguments parser.

Builds an ``argparse.ArgumentParser`` from a function's parameters and
docstring, and calls it with the program arguments already parsed:

* The docstring text describes the program.
* Docstring parameter descriptions describe program arguments.
* A non-keyword parameter is converted to a positional argument.
* A keyword parameter is converted to an optional argument.

  * An argument type is taken from its parameter docstring type. If it looks
    like a fully qualified path then the module/package is imported first,
    otherwise the builtins module is used. If unspecified the type is inferred
    from its default value. If its default value is ``None`` then it defaults
    to ``six.text_type``.
  * A boolean parameter is converted to a flag argument. When present in
    the command line its default value is negated via a logical ``not``.
  * A short option is automatically created from the first available
    character of its name.
  * The parameter's docstring type and the default value's inferred type
    don't need to match, but the latter is required to be a subclass of
    the former.
"""


# External:
import argparse


__all__ = ['start']


class AmbiguousDesc (Error):
    def __str__(self):
        return 'custom arg parser instance has a description already'


def add_options(arg_parser, arguments):
    """
    Converts arguments to ``argparse`` options and adds them.

    :type arg_parser: argparse.ArgumentParser
    :type arguments: iterable<Argument>
    """

    for argument in arguments:
        names = []
        options = {}

        if argument.description is not None:
            options['help'] = argument.description

        if argument.has_default_value:
            if argument.short_name is not None:
                names.append(arg_parser.prefix_chars + argument.short_name)

            data_type = argument.extract_data_type()
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


def start(main,
        args = None,
        arg_parser = None,
        soft_errors = True):
    """
    Starts a function, passing to it program arguments parsed via ``argparse``.

    :param main: entry point
    :type main: callable
    :param args: program arguments, otherwise leaves it up to
        ``argparse.ArgumentParser.parse_args()`` to define
    :type args: list<six.string_types>
    :param arg_parser: user defined argument parser
    :type arg_parser: argparse.ArgumentParser
    :param soft_errors: if true converts parsing exceptions to error messages
        for ``argparse.ArgumentParser.error()``
    :type soft_errors: bool
    :return: entry point's return value
    """

    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    try:
        arguments = extract_arguments(main)
        description = parse_docstring(main, arguments)

        if description is not None:
            if arg_parser.description is None:
                arg_parser.description = description
            else:
                raise AmbiguousDesc()

        add_options(arg_parser, arguments)
    except Error as error:
        if soft_errors:
            arg_parser.error(error)
        else:
            raise
    else:
        return main(**arg_parser.parse_args(args = args).__dict__)
'''
