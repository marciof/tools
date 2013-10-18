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


    def test_empty_param_description(self):
        def f():
            """
            :param x:
            """

        with self.assertRaisesRegexp(argf.UndefinedParamDesc, r'\bx\b'):
            argf.extract_documentation(f)


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


    def test_unicode(self):
        def f():
            """
            Main description.

            :param x: param description
            :type x: int
            """

        (main_desc, data_types, descriptions) = argf.extract_documentation(f)

        self.assertIsInstance(main_desc, six.text_type)

        self.assertEqual(
            tuple(map(type, data_types.keys())),
            (six.text_type,))

        self.assertEqual(
            tuple(map(type, descriptions.keys())),
            (six.text_type,))

        self.assertEqual(
            tuple(map(type, descriptions.values())),
            (six.text_type,))


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


    def test_unicode(self):
        def f(x):
            pass

        [name] = argf.extract_parameters(f)
        self.assertIsInstance(name, six.text_type)
