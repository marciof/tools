# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import collections
import sys

# External:
import six

# Internal:
import argf
from tests import unittest


class ClassForLoadingTest:
    class Inner:
        pass


class TestArgumentExtraction (unittest.TestCase):
    def test_compatible_data_types(self):
        def f(length = True):
            """
            :type length: int
            """

        (desc, [arg]) = argf.extract_arguments(f)

        self.assertIsInstance(arg, argf.OptionArgument)
        self.assertIs(arg.get_actual_data_type(), int)

        self.assertEqual(arg.name, 'length')
        self.assertIs(arg.data_type, int)
        self.assertIs(arg.description, None)
        self.assertIs(arg.default_value, True)


    def test_default_data_type(self):
        def f(name):
            """
            :param name: description
            """
            pass

        (desc, [arg]) = argf.extract_arguments(f)

        self.assertIsInstance(arg, argf.Argument)
        self.assertIs(arg.get_actual_data_type(), six.text_type)

        self.assertEqual(arg.name, 'name')
        self.assertIs(arg.data_type, None)
        self.assertEqual(arg.description, 'description')


    def test_incompatible_data_types(self):
        def f(verbose = 1):
            """
            :type verbose: bool
            """

        (desc, [arg]) = argf.extract_arguments(f)

        self.assertIsInstance(arg, argf.OptionArgument)
        self.assertEqual(arg.name, 'verbose')
        self.assertIs(arg.data_type, bool)
        self.assertIs(arg.description, None)
        self.assertIs(arg.default_value, 1)

        with self.assertRaisesRegex(
                argf.IncompatibleParamDataTypes,
                r'\bverbose\b'):

            self.assertIs(arg.get_actual_data_type(), int)


    def test_inferred_data_type(self):
        def f(verbose = True):
            pass

        (desc, [arg]) = argf.extract_arguments(f)

        self.assertIsInstance(arg, argf.OptionArgument)
        self.assertIs(arg.get_actual_data_type(), bool)

        self.assertEqual(arg.name, 'verbose')
        self.assertIs(arg.data_type, None)
        self.assertIs(arg.description, None)
        self.assertIs(arg.default_value, True)


    def test_name_translation(self):
        def f(class_, default_name):
            pass

        (desc, [class_arg, def_name_arg]) = argf.extract_arguments(f)

        self.assertEqual(class_arg.get_actual_name(), 'class')
        self.assertEqual(def_name_arg.get_actual_name(), 'default-name')


    def test_none_as_default_value(self):
        def f(length = None):
            """
            :type length: int
            :param length: description
            """

        (desc, [arg]) = argf.extract_arguments(f)

        self.assertIsInstance(arg, argf.OptionArgument)
        self.assertIs(arg.get_actual_data_type(), int)

        self.assertEqual(arg.name, 'length')
        self.assertIs(arg.data_type, int)
        self.assertEqual(arg.description, 'description')
        self.assertIs(arg.default_value, None)


    def test_unknown(self):
        def description(length):
            """
            :param verbose: sample description
            """

        def data_type(name):
            """
            :type default: int
            """

        with self.assertRaisesRegex(argf.UnknownParams, r'\bverbose\b'):
            argf.extract_arguments(description)

        with self.assertRaisesRegex(argf.UnknownParams, r'\bdefault\b'):
            argf.extract_arguments(data_type)


class TestDataTypeLoading (unittest.TestCase):
    def setUp(self):
        self.module = sys.modules[__name__]


    def test_builtin(self):
        self.assertIs(
            argf.load_type('int', self.module),
            int)


    def test_from_module(self):
        self.assertIs(
            argf.load_type('collections.defaultdict', self.module),
            collections.defaultdict)


    def test_from_unknown_module(self):
        with self.assertRaisesRegex(argf.UnknownParamDataType, '.'):
            argf.load_type('does_not_exist.defaultdict', self.module)


    def test_global(self):
        self.assertIs(
            argf.load_type('ClassForLoadingTest', self.module),
            ClassForLoadingTest)


    def test_inner(self):
        self.assertIs(
            argf.load_type('ClassForLoadingTest.Inner', self.module),
            ClassForLoadingTest.Inner)


    def test_invalid(self):
        with self.assertRaisesRegex(argf.UnknownParamDataType, '.'):
            argf.load_type('collections.namedtuple', self.module)


    def test_unknown(self):
        with self.assertRaisesRegex(argf.UnknownParamDataType, '.'):
            argf.load_type('does_not_exist', self.module)


class TestDocumentationExtraction (unittest.TestCase):
    def test_ambiguous_param_data_type(self):
        def f():
            """
            :type x: list
            :type x: dict
            """

        with self.assertRaisesRegex(argf.AmbiguousParamDataType, r'\bx\b'):
            argf.extract_documentation(f)


    def test_ambiguous_param_description(self):
        def f():
            """
            :param x: this
            :param x: that
            """

        with self.assertRaisesRegex(argf.AmbiguousParamDesc, r'\bx\b'):
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


    def test_empty_param_data_type(self):
        def f():
            """
            :type x:
            """

        with self.assertRaisesRegex(argf.UndefinedParamDataType, r'\bx\b'):
            argf.extract_documentation(f)


    def test_empty_param_description(self):
        def f():
            """
            :param x:
            """

        with self.assertRaisesRegex(argf.UndefinedParamDesc, r'\bx\b'):
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


    def test_no_documentation(self):
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


    def test_unknown_directive(self):
        def no_arg():
            """
            :unknown: xyz
            """

        def single_arg():
            """
            :unknown abc: xyz
            """

        self.assertEqual(
            argf.extract_documentation(no_arg),
            (None, {}, {}))

        self.assertEqual(
            argf.extract_documentation(single_arg),
            (None, {}, {}))


class TestParameterExtraction (unittest.TestCase):
    def test_dynamic(self):
        def args(*args):
            pass

        def kwargs(**kwargs):
            pass

        with self.assertRaisesRegex(argf.DynamicArgs, '.'):
            argf.extract_parameters(args)

        with self.assertRaisesRegex(argf.DynamicArgs, '.'):
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


    try:
        eval('lambda (x,): None')
    except SyntaxError:
        pass
    else:
        def test_tuple(self):
            f = eval('lambda (x, y): None')

            with self.assertRaisesRegex(argf.TupleArg, r'\(x, y\)'):
                argf.extract_parameters(f)


if __name__ == '__main__':
    # Standard:
    import os.path

    unittest.main(os.path.splitext(os.path.basename(__file__))[0])
