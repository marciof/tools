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


class UndefinedParamDesc (Error):
    def __str__(self):
        return 'undefined parameter description: %s' % self.args


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
        raise UnknownParams(set(data_types.keys()).union(descriptions.keys()))

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
    :raise UndefinedParamDesc:
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
        name = six.text_type(name)

        if kind == 'param':
            if name in descriptions:
                raise AmbiguousParamDesc(name)
            elif field_body is None:
                raise UndefinedParamDesc(name)
            else:
                descriptions[name] = six.text_type(field_body)
        elif kind == 'type':
            if name in data_types:
                raise AmbiguousParamDataType(name)
            else:
                data_types[name] = load_data_type(field_body)

    main_desc = doc.findtext('paragraph')

    if main_desc is not None:
        main_desc = six.text_type(main_desc)

    return (main_desc, data_types, descriptions)


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
        name = six.text_type(name)
        kwarg_i = arg_i - kwargs_offset
        is_keyword = (0 <= kwarg_i < nr_kwargs)

        if is_keyword:
            params.append((name, arg_spec.defaults[kwarg_i]))
        else:
            params.append(name)

    return params


def load_data_type(name):
    """
    :type name: six.string_types
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
