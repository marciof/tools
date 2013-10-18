# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import collections
import unittest2

# Internal:
import argf

# External:
import six


class TestArgumentExtraction (unittest2.TestCase):
    def test_argument(self):
        def f(x):
            """
            :param x: sample description
            :type x: int
            """

        (desc, [arg]) = argf.extract_arguments(f)

        self.assertIsInstance(arg, argf.Argument)
        self.assertEqual(arg.name, 'x')
        self.assertEqual(arg.data_type, int)
        self.assertEqual(arg.description, 'sample description')


    def test_option_argument(self):
        def f(x = 123):
            """
            :param x: sample description
            :type x: int
            """

        (desc, [arg]) = argf.extract_arguments(f)

        self.assertIsInstance(arg, argf.OptionArgument)
        self.assertEqual(arg.name, 'x')
        self.assertEqual(arg.data_type, int)
        self.assertEqual(arg.description, 'sample description')
        self.assertEqual(arg.default_value, 123)


    def test_unknown(self):
        def description(x):
            """
            :param y: sample description
            """

        def data_type(x):
            """
            :type z: int
            """

        with self.assertRaisesRegexp(argf.UnknownParams, r'\by\b'):
            argf.extract_arguments(description)

        with self.assertRaisesRegexp(argf.UnknownParams, r'\bz\b'):
            argf.extract_arguments(data_type)


class TestArgumentValidation (unittest2.TestCase):
    def test_compatible_data_types(self):
        def f(x = True):
            """
            :type x: int
            """

        (desc, [arg]) = argf.extract_arguments(f)
        self.assertEqual(arg.data_type, int)


    def test_default_data_type(self):
        def f(x = 'text'):
            pass

        (desc, [arg]) = argf.extract_arguments(f)
        self.assertEqual(arg.data_type, six.text_type)


    def test_incompatible_data_types(self):
        def f(x = 1):
            """
            :type x: bool
            """

        with self.assertRaisesRegexp(argf.IncompatibleParamDataTypes, r'\bx\b'):
            argf.extract_arguments(f)


    def test_none_as_default_value(self):
        def f(x = None):
            """
            :type x: int
            """

        (desc, [arg]) = argf.extract_arguments(f)
        self.assertEqual(arg.data_type, int)


class TestDataTypeLoading (unittest2.TestCase):
    def test_builtin(self):
        self.assertIs(argf.load_data_type('int'), int)


    def test_from_module(self):
        self.assertIs(
            argf.load_data_type('collections.namedtuple'),
            collections.namedtuple)


    def test_from_unknown_module(self):
        with self.assertRaises(argf.ParamDataTypeImportError):
            argf.load_data_type('collection.namedtuple')


    def test_unknown(self):
        with self.assertRaises(argf.UnknownParamDataType):
            argf.load_data_type('string')


class TestDocumentationExtraction (unittest2.TestCase):
    def test_ambiguous_param_data_type(self):
        def f():
            """
            :type x: list
            :type x: dict
            """

        with self.assertRaisesRegexp(argf.AmbiguousParamDataType, r'\bx\b'):
            argf.extract_documentation(f)


    def test_ambiguous_param_description(self):
        def f():
            """
            :param x: this
            :param x: that
            """

        with self.assertRaisesRegexp(argf.AmbiguousParamDesc, r'\bx\b'):
            argf.extract_documentation(f)


    def test_description(self):
        def f():
            """
            Example program.
            """

        self.assertEqual(
            argf.extract_documentation(f),
            ('Example program.', {}, {}))


    def test_empty(self):
        def f():
            """
            """

        self.assertEqual(argf.extract_documentation(f), (None, {}, {}))


    def test_full(self):
        def f():
            """
            Program description.

            :param x: param description
            :type x: dict
            """

        self.assertEqual(
            argf.extract_documentation(f),
            ('Program description.', {'x': dict}, {'x': 'param description'}))


    def test_none(self):
        def f():
            pass

        self.assertEqual(argf.extract_documentation(f), (None, {}, {}))


    def test_param_data_type(self):
        def f():
            """
            :type x: list
            :type y: dict
            """

        self.assertEqual(
            argf.extract_documentation(f),
            (None, {'x': list, 'y': dict}, {}))


    def test_param_description(self):
        def f():
            """
            :param x: this
            :param y: that
            """

        self.assertEqual(
            argf.extract_documentation(f),
            (None, {}, {'x': 'this', 'y': 'that'}))


class TestParameterExtraction (unittest2.TestCase):
    def test_dynamic(self):
        def args(*args):
            pass

        def kwargs(**kwargs):
            pass

        with self.assertRaises(argf.DynamicArgs):
            argf.extract_parameters(args)

        with self.assertRaises(argf.DynamicArgs):
            argf.extract_parameters(kwargs)


    def test_empty(self):
        def f():
            pass

        self.assertEqual(argf.extract_parameters(f), [])


    def test_keyword(self):
        def f(x = True, y = None):
            pass

        self.assertEqual(
            argf.extract_parameters(f),
            [('x', True), ('y', None)])


    def test_positional(self):
        def f(x, y):
            pass

        self.assertEqual(argf.extract_parameters(f), ['x', 'y'])


    def test_mixed(self):
        def f(x, y, z = False):
            pass

        self.assertEqual(
            argf.extract_parameters(f),
            ['x', 'y', ('z', False)])


'''
# External:
import argparse


class Error (Exception):
    pass


class HelpPrinted (Exception):
    pass


class ArgumentParser (argparse.ArgumentParser):
    def error(self, message):
        raise Error(message)


    def print_help(self, file = None):
        text = six.StringIO()

        argparse.ArgumentParser.print_help(self, text)
        raise HelpPrinted(text.getvalue())


FEW_ARGS_ERR_RE = 'few arguments' if six.PY2 else 'arguments are required:'
OPT_ARGS_RE = 'optional arguments:'
UNK_ARGS_ERR_RE = 'unrecognized arguments'


def start(*args, **kwargs):
    kwargs.setdefault('args', [])

    if 'arg_parser' not in kwargs:
        kwargs['arg_parser'] = ArgumentParser()

    return argf.start(*args,
        soft_errors = False,
        **kwargs)


class TestParameters (unittest2.TestCase):
    def test_boolean_option(self):
        def main(verbose = False):
            return verbose

        self.assertEqual(start(main), False)
        self.assertEqual(start(main, args = ['-v']), True)
        self.assertEqual(start(main, args = ['--verbose']), True)

        with self.assertRaisesRegexp(Error, UNK_ARGS_ERR_RE):
            start(main, args = ['--verbose', 'False'])


    def test_default_options(self):
        def main():
            return 123

        with self.assertRaisesRegexp(HelpPrinted, OPT_ARGS_RE):
            start(main, args = ['-h'])

        with self.assertRaisesRegexp(HelpPrinted, OPT_ARGS_RE):
            start(main, args = ['--help'])

        with self.assertRaisesRegexp(Error, UNK_ARGS_ERR_RE):
            start(main,
                args = ['-h'],
                arg_parser = ArgumentParser(add_help = False))


    def test_integer_option(self):
        def main(length = 123):
            return length

        self.assertEqual(start(main), 123)
        self.assertEqual(start(main, args = ['-l', '321']), 321)
        self.assertEqual(start(main, args = ['--length', '321']), 321)

        with self.assertRaisesRegexp(Error, 'length: invalid'):
            start(main, args = ['--length', 'guest'])

        with self.assertRaisesRegexp(Error, UNK_ARGS_ERR_RE):
            start(main, args = ['--size', '321'])


    def test_no_arguments(self):
        def main():
            return 123

        self.assertEqual(start(main), 123)

        with self.assertRaisesRegexp(Error, UNK_ARGS_ERR_RE):
            start(main, args = ['123'])


    def test_none_type_option(self):
        def main(user = None):
            return user

        self.assertEqual(start(main), None)
        self.assertEqual(start(main, args = ['-u', 'guest']), 'guest')
        self.assertEqual(start(main, args = ['--user', 'test']), 'test')


    def test_custom_prefix_chars(self):
        def main(user = 'guest'):
            return user

        for option in ['/u', '//user']:
            self.assertEqual(
                start(main,
                    args = [option, 'test'],
                    arg_parser = ArgumentParser(prefix_chars = '/')),
                'test')


    def test_single_argument(self):
        def main(user):
            return user

        with self.assertRaisesRegexp(Error, FEW_ARGS_ERR_RE):
            start(main)

        self.assertEqual(start(main, args = ['guest']), 'guest')

        with self.assertRaisesRegexp(Error, UNK_ARGS_ERR_RE):
            start(main, args = ['guest', 'test'])


    def test_string_option(self):
        def main(user = 'guest'):
            return user

        self.assertEqual(start(main), 'guest')
        self.assertEqual(start(main, args = ['-u', 'test']), 'test')
        self.assertEqual(start(main, args = ['--user', 'test']), 'test')


    def test_varargs(self):
        def main_varargs(*args):
            return args

        def main_kwargs(**kwargs):
            return kwargs

        with self.assertRaises(argf.DynamicArgs):
            start(main_varargs)

        with self.assertRaises(argf.DynamicArgs):
            start(main_kwargs)


class TestDocstring (unittest2.TestCase):
    def test_ambiguous_parameter_description(self):
        def main(user):
            """
            :param user: user name
            :param user: full name
            """
            return user

        with self.assertRaisesRegexp(argf.AmbiguousParamDesc, 'user'):
            start(main, args = ['guest'])


    def test_ambiguous_parameter_type(self):
        def main(user):
            """
            :type user: six.binary_type
            :type user: six.text_type
            """
            return user

        with self.assertRaisesRegexp(argf.AmbiguousParamDataType, 'user'):
            start(main, args = ['guest'])


    def test_incompatible_types(self):
        def main(user = 'guest'):
            """:type user: int"""
            return user

        with self.assertRaisesRegexp(argf.IncompatibleTypes, 'user'):
            start(main)


    def test_invalid_type(self):
        def main_global(user):
            """:type user: string"""
            return user

        def main_package(user):
            """:type user: x.y"""
            return user

        with self.assertRaisesRegexp(argf.UnknownParamDataType, 'string'):
            start(main_global, args = ['guest'])

        with self.assertRaisesRegexp(argf.ParamDataTypeImportError, 'x.y'):
            start(main_package, args = ['guest'])


    def test_name_mismatch(self):
        def main_param(user):
            """:param name: user name"""
            return user

        def main_type(user):
            """:type name: six.text_type"""
            return user

        with self.assertRaisesRegexp(argf.UnknownParam, 'name'):
            start(main_param, args = ['guest'])

        with self.assertRaisesRegexp(argf.UnknownParam, 'name'):
            start(main_type, args = ['guest'])


    def test_none_type_option(self):
        def main(length = None):
            """:type length: int"""
            return length

        self.assertEqual(start(main), None)
        self.assertEqual(start(main, args = ['-l', '123']), 123)
        self.assertEqual(start(main, args = ['--length', '321']), 321)


    def test_parameter_description(self):
        def main(user):
            """:param user: full user name"""
            return user

        with self.assertRaisesRegexp(HelpPrinted, 'full user name'):
            start(main, args = ['-h'])


    def test_program_description(self):
        def main():
            """does nothing"""
            return 123

        def main_none():
            return 321

        with self.assertRaisesRegexp(HelpPrinted, 'does nothing'):
            start(main, args = ['-h'])

        with self.assertRaises(argf.AmbiguousDesc):
            start(main, arg_parser = ArgumentParser(description = 'duplicate'))

        with self.assertRaisesRegexp(HelpPrinted, 'alternate'):
            start(main_none,
                args = ['-h'],
                arg_parser = ArgumentParser(description = 'alternate'))
'''
