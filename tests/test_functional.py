#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import contextlib
import sys

# Standard/External:
import argparse

# External:
import six

# Internal:
import argf
import tests


class Error (Exception):
    pass


class Help (Exception):
    pass


class ArgumentParser (argparse.ArgumentParser):
    def error(self, message):
        raise Error(message)


    def print_help(self, file = None):
        message = six.StringIO()
        argparse.ArgumentParser.print_help(self, file = message)
        raise Help(message.getvalue())


def start(*args, **kwargs):
    kwargs.setdefault('args', [])

    if 'arg_parser' not in kwargs:
        kwargs['arg_parser'] = ArgumentParser()

    return argf.start(*args, soft_errors = False, **kwargs)


class TestDistribution (tests.TestCase):
    def test_features(self):
        self.assertIsInstance(argf.__features__, frozenset)
        self.assertEquals(argf.__features__, frozenset())


    def test_version_tuple(self):
        self.assertIsInstance(argf.__version__, tuple)
        self.assertGreaterEqual(len(argf.__version__), 1)

        for part in argf.__version__:
            self.assertIsInstance(part, int)


class TestArguments (tests.TestCase):
    def test_argument_help(self):
        def main(length, user_name = 'guest'):
            """
            :param length: number of elements
            :param user_name: full username
            """
            return user_name

        with self.assertRaisesRegex(Help, r'\bnumber of elements\b'):
            start(main, args = ['-h'])

        with self.assertRaisesRegex(Help, r'\bfull username\b'):
            start(main, args = ['-h'])


    def test_error_handling(self):
        def main():
            """
            :param user: user name
            """

        with self.assertRaises(SystemExit):
            with contextlib.closing(six.StringIO()) as sys.stderr:
                argf.start(main, args = [])


    def test_no_arguments(self):
        def main():
            return 123

        self.assertEqual(start(main), 123)

        with self.assertRaises(Error):
            start(main, args = ['123'])


    def test_program_help(self):
        def main_with():
            """
            Sample description.
            """
            return 123

        def main_without():
            return 321

        with self.assertRaisesRegex(Help, r'\bSample description\.'):
            start(main_with, args = ['-h'])

        with self.assertRaisesRegex(argf.AmbiguousDesc, '.'):
            start(main_with,
                arg_parser = ArgumentParser(description = 'Duplicate.'))

        with self.assertRaisesRegex(Help, r'\bAlternate\.'):
            start(main_without,
                args = ['-h'],
                arg_parser = ArgumentParser(description = 'Alternate.'))


class TestOptionalArguments (tests.TestCase):
    def test_boolean_argument(self):
        def main(verbose = False):
            return verbose

        self.assertEqual(start(main), False)
        self.assertEqual(start(main, args = ['-v']), True)
        self.assertEqual(start(main, args = ['--verbose']), True)

        with self.assertRaises(Error):
            start(main, args = ['--verbose', 'False'])


    def test_help_argument(self):
        def main():
            return 123

        with self.assertRaises(Help):
            start(main, args = ['-h'])

        with self.assertRaises(Help):
            start(main, args = ['--help'])

        with self.assertRaises(Error):
            start(main,
                args = ['-h'],
                arg_parser = ArgumentParser(add_help = False))


    def test_integer_argument(self):
        def main(length = 123):
            return length

        self.assertEqual(start(main), 123)
        self.assertEqual(start(main, args = ['-l', '321']), 321)
        self.assertEqual(start(main, args = ['--length', '321']), 321)

        with self.assertRaises(Error):
            start(main, args = ['--length', 'text'])


    def test_none_as_default_value(self):
        def main(user_name = None):
            """
            :type user_name: int
            """
            return user_name

        self.assertEqual(start(main), None)
        self.assertEqual(start(main, args = ['-u', '123']), 123)
        self.assertEqual(start(main, args = ['--user-name', '321']), 321)


    def test_prefix_chars(self):
        def main(user_name = 'guest'):
            return user_name

        self.assertEqual(
            start(main,
                args = ['/u', 'test'],
                arg_parser = ArgumentParser(prefix_chars = '/')),
            'test')

        self.assertEqual(
            start(main,
                args = ['//user-name', 'test'],
                arg_parser = ArgumentParser(prefix_chars = '/')),
            'test')


    def test_short_option_generation(self):
        def main(user = 'guest', uname = 'linux', huh = True):
            return (user, uname, huh)

        self.assertEqual(start(main), ('guest', 'linux', True))

        self.assertEqual(
            start(main, args = ['-u', 'test']),
            ('test', 'linux', True))

        self.assertEqual(
            start(main, args = ['-n', 'windows']),
            ('guest', 'windows', True))

        self.assertEqual(
            start(main, args = ['--huh']),
            ('guest', 'linux', False))


    def test_string_argument(self):
        def main(user_name = 'guest'):
            return user_name

        self.assertEqual(start(main), 'guest')
        self.assertEqual(start(main, args = ['-u', 'test']), 'test')
        self.assertEqual(start(main, args = ['--user-name', '123']), '123')


class TestPositionalArguments (tests.TestCase):
    def test_boolean_argument(self):
        def main(debug):
            """
            :type debug: bool
            """
            return debug

        self.assertEqual(start(main, args = ['x']), True)
        self.assertEqual(start(main, args = ['']), False)

        with self.assertRaises(Error):
            start(main)


    def test_integer_argument(self):
        def main(length):
            """
            :type length: int
            """
            return length

        self.assertEqual(start(main, args = ['321']), 321)

        with self.assertRaises(Error):
            start(main)

        with self.assertRaises(Error):
            start(main, args = ['text'])


    def test_string_argument(self):
        def main(user_name):
            return user_name

        self.assertEqual(start(main, args = ['test']), 'test')
        self.assertEqual(start(main, args = ['123']), '123')

        with self.assertRaises(Error):
            start(main)
