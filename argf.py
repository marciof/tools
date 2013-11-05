# -*- coding: UTF-8 -*-


"""
Declarative command line arguments parser.

Builds options for an ``argparse.ArgumentParser`` from a function's
parameters and docstring, and calls it with the program arguments already
parsed.

* The docstring text describes the program.
* Docstring parameter descriptions describe program arguments.
* A non-keyword parameter is converted to a positional argument.
* A keyword parameter is converted to an optional argument.

Argument conversions:

* An argument type is taken from its parameter docstring type. If it's a
  fully qualified path then the module/package is imported first, otherwise
  the builtins module is used. If unspecified, the type is inferred from
  its default value (if it has one and if it's not ``None``), otherwise
  defaults to ``six.text_type``.
* A boolean keyword parameter is converted to a flag argument. When present
  in the command line its default value is negated via a logical ``not``.
* A short option is automatically created from the first character not
  already in use of a keyword argument's name.
* A keyword parameter's default value, if not ``None``, is required to be
  an instance of the argument type.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
inspect = None # lazy
import re

# External:
argparse = None # lazy
docutils_core = None # lazy
docutils_nodes = None # lazy
six = None # lazy


__all__ = ['start']
__version__ = (0, 1, 0) # semver


# TODO: Use the ``python_2_unicode_compatible`` decorator for ``__unicode__``?
class Error (Exception):
    pass


class AmbiguousDesc (Error):
    def __str__(self):
        return 'user defined arg parser instance already has a description'


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
        (name, error) = self.args
        return 'failed to import parameter data type: %s: %s' % (name, error)


class UndefinedParamDataType (Error):
    def __str__(self):
        return 'undefined parameter data type: %s' % self.args


class UndefinedParamDesc (Error):
    def __str__(self):
        return 'undefined parameter description: %s' % self.args


class UnknownParams (Error):
    def __str__(self):
        (names,) = self.args
        return 'unknown parameter(s): ' + ', '.join(sorted(names))


class UnknownParamDataType (Error):
    def __str__(self):
        return 'unknown parameter data type: %s' % self.args


class TupleArg (Error):
    def __str__(self):
        (arg,) = self.args
        return 'tuple argument (parameter unpacking) is not supported: (%s)' \
            % ', '.join(arg)


class Argument (object):
    _WORD_SEPARATOR = '-'


    def __init__(self, name):
        self.name = name
        self.data_type = None
        self.description = None


    def add_to_parser(self, arg_parser):
        """
        :type arg_parser: argparse.ArgumentParser
        """

        options = {
            'metavar': self.get_actual_name(),
            'type': self.get_actual_data_type(),
        }

        if self.description is not None:
            options['help'] = self.description

        arg_parser.add_argument(self.name, **options)


    def get_actual_data_type(self):
        global six
        if six is None: # pragma: no cover
            import six

        if self.data_type is None:
            return six.text_type
        else:
            return self.data_type


    def get_actual_name(self):
        return self.name.strip('_').replace('_', self._WORD_SEPARATOR)


class OptionArgument (Argument):
    def __init__(self, name, default_value):
        Argument.__init__(self, name)
        self.default_value = default_value


    def add_to_parser(self, arg_parser):
        """
        :type arg_parser: argparse.ArgumentParser
        """

        actual_name = self.get_actual_name()
        data_type = self.get_actual_data_type()
        names = [(2 * arg_parser.prefix_chars) + actual_name]

        options = {
            'default': self.default_value,
            'dest': self.name,
        }

        if self.description is not None:
            options['help'] = self.description

        if issubclass(data_type, bool):
            options['const'] = not self.default_value
            options['action'] = 'store_const'
        else:
            options['type'] = data_type

        reserved_chars = set([self._WORD_SEPARATOR])

        # TODO: Don't use undocumented functions.
        for option in arg_parser._option_string_actions.keys():
            if (len(option) == 2) and (option[0] == arg_parser.prefix_chars):
                reserved_chars.add(option[1])

        available_chars = actual_name.translate(
            dict((ord(ch), '') for ch in reserved_chars))

        if len(available_chars) > 0:
            names.append(arg_parser.prefix_chars + available_chars[0])

        arg_parser.add_argument(*names, **options)


    def get_actual_data_type(self):
        """
        :raise IncompatibleParamDataTypes:
        """

        if self.default_value is None:
            return Argument.get_actual_data_type(self)
        elif self.data_type is None:
            return type(self.default_value)
        elif not isinstance(self.default_value, self.data_type):
            raise IncompatibleParamDataTypes(self.name)
        else:
            return self.data_type


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
            arg = Argument(name = param)

        if arg.name in data_types:
            arg.data_type = data_types.pop(arg.name)

        if arg.name in descriptions:
            arg.description = descriptions.pop(arg.name)

        args.append(arg)

    if (len(data_types) > 0) or (len(descriptions) > 0):
        raise UnknownParams(set(data_types.keys()).union(descriptions.keys()))

    return (main_desc, args)


# TODO: Leverage Sphinx for parsing, but provide a fallback?
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

    global inspect
    if inspect is None: # pragma: no cover
        import inspect

    docstring = inspect.getdoc(function)

    if docstring is None:
        return (None, data_types, descriptions)

    global docutils_core
    if docutils_core is None: # pragma: no cover
        import docutils.core as docutils_core

    global docutils_nodes
    if docutils_nodes is None: # pragma: no cover
        import docutils.nodes as docutils_nodes
    
    global six
    if six is None: # pragma: no cover
        import six

    doc = docutils_core.publish_doctree(docstring)

    for field in doc.traverse(docutils_nodes.field):
        [field_name] = field.traverse(docutils_nodes.field_name)
        directive = re.match(r'^(\w+)\s+([^\s]*)$', field_name.astext())

        if directive is None:
            continue

        (kind, name) = directive.groups()
        name = six.text_type(name)

        field_body = field.traverse(docutils_nodes.paragraph)

        if len(field_body) == 0:
            field_body = None
        else:
            [field_body] = field_body
            field_body = field_body.astext()

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
            elif field_body is None:
                raise UndefinedParamDataType(name)
            else:
                data_types[name] = load_data_type(field_body)

    main_desc = doc.traverse(lambda node:
        isinstance(node, docutils_nodes.paragraph) and (node.parent is doc))
    
    if len(main_desc) == 0:
        main_desc = None
    else:
        [main_desc] = main_desc
        main_desc = six.text_type(main_desc.astext())

    return (main_desc, data_types, descriptions)


# TODO: Support list options? Via type ``list``? Via varargs?
# TODO: Support sub-commands via enum parameters?
def extract_parameters(function):
    """
    :type function: types.FunctionType
    :rtype: list<six.text_type | tuple<six.text_type, object>>
    :raise DynamicArgs:
    :raise TupleArg:
    """

    global inspect
    if inspect is None: # pragma: no cover
        import inspect

    arg_spec = inspect.getargspec(function)

    if (arg_spec.varargs is not None) or (arg_spec.keywords is not None):
        raise DynamicArgs()

    nr_kwargs = 0 if arg_spec.defaults is None else len(arg_spec.defaults)
    kwargs_offset = len(arg_spec.args) - nr_kwargs
    params = []

    global six
    if six is None: # pragma: no cover
        import six

    for name, arg_i in zip(arg_spec.args, range(len(arg_spec.args))):
        if not isinstance(name, six.string_types):
            raise TupleArg(name)

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
    :type name: six.text_type
    :rtype: six.class_types
    """

    if '.' not in name:
        global six
        if six is None: # pragma: no cover
            import six

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


# TODO: Add a version argument from `__version__`?
def start(main,
        args = None,
        arg_parser = None,
        soft_errors = True):
    
    """
    Starts a function with program arguments parsed via ``argparse``.

    :type main: types.FunctionType
    :param main: entry point
    :type args: list<six.text_type>
    :param args: user defined program arguments, otherwise leaves it up to
        ``argparse.ArgumentParser.parse_args()`` to define
    :type arg_parser: argparse.ArgumentParser
    :param arg_parser: user defined argument parser
    :type soft_errors: bool
    :param soft_errors: if true, catches parsing exceptions and converts
        them to error messages for ``argparse.ArgumentParser.error()``
    :return: entry point's return value
    """

    if arg_parser is None:
        global argparse
        if argparse is None: # pragma: no cover
            import argparse

        arg_parser = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    try:
        (description, arguments) = extract_arguments(main)

        if description is not None:
            if arg_parser.description is None:
                arg_parser.description = description
            else:
                raise AmbiguousDesc()

        for argument in arguments:
            argument.add_to_parser(arg_parser)
    except Error as error:
        if soft_errors:
            arg_parser.error(error)
        else:
            raise
    else:
        return main(**vars(arg_parser.parse_args(args = args)))
