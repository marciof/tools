# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import collections
import unittest2

# Internal:
import argf


class TestDataTypeLoading (unittest2.TestCase):
    def test_builtin(self):
        self.assertIs(
            argf.load_data_type('int'),
            int)


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


'''
# External:
import argparse
import six


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
