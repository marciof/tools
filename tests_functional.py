# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import unittest2

# External:
import argparse
import six

# Internal:
import argf


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


class TestOptionalArguments (unittest2.TestCase):
    def test_argument_help(self):
        def main(user_name = 'guest'):
            """
            :param user_name: full username
            """
            return user_name

        with self.assertRaisesRegexp(Help, r'\bfull username\b'):
            start(main, args = ['-h'])


    def test_boolean_type(self):
        def main(verbose = False):
            return verbose

        self.assertEqual(start(main), False)
        self.assertEqual(start(main, args = ['-v']), True)
        self.assertEqual(start(main, args = ['--verbose']), True)

        with self.assertRaises(Error):
            start(main, args = ['--verbose', 'False'])


    def test_help_option(self):
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


    def test_integer_type(self):
        def main(length = 123):
            return length

        self.assertEqual(start(main), 123)
        self.assertEqual(start(main, args = ['-l', '321']), 321)
        self.assertEqual(start(main, args = ['--length', '321']), 321)

        with self.assertRaises(Error):
            start(main, args = ['--length', 'text'])


    def test_none_value(self):
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
        def main(user = 'guest', uname = 'linux'):
            return (user, uname)

        self.assertEqual(start(main), ('guest', 'linux'))

        self.assertEqual(
            start(main, args = ['-u', 'test']),
            ('test', 'linux'))

        self.assertEqual(
            start(main, args = ['-n', 'windows']),
            ('guest', 'windows'))


    def test_string_type(self):
        def main(user_name = 'guest'):
            return user_name

        self.assertEqual(start(main), 'guest')
        self.assertEqual(start(main, args = ['-u', 'test']), 'test')
        self.assertEqual(start(main, args = ['--user-name', '123']), '123')
