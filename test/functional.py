#!/usr/bin/env python3

import os
import subprocess
import unittest

BINARY = ['valgrind', '-q', '--leak-check=yes', './show']

def popen(args, stdout = subprocess.PIPE, stdin = None):
    if isinstance(stdin, subprocess.Popen):
        stdin = stdin.stdout

    return subprocess.Popen(args,
        stdin = stdin,
        stdout = stdout,
        stderr = subprocess.PIPE)

def get_test_directory():
    return '/'

def get_test_file():
    return __file__

class TestPipePlugin (unittest.TestCase):
    def test_directory(self):
        directory = get_test_directory()
        directory_fd = os.open(directory, os.O_RDONLY)

        try:
            process = popen(BINARY, stdin = directory_fd)
            (out, err) = process.communicate()

            ls = popen(['ls', directory])
            (ls_out, ls_err) = ls.communicate()

            self.assertEqual(process.returncode, 0)
            self.assertEqual(process.returncode, ls.returncode)

            self.assertEqual(out, ls_out)
            self.assertEqual(err, ls_err)
            self.assertEqual(err, b'')
        finally:
            os.close(directory_fd)

    def test_file(self):
        with open(get_test_file(), 'rb') as f:
            text = f.read()
            f.seek(0)

            process = popen(BINARY, stdin = f)
            (out, err) = process.communicate()

            self.assertEqual(process.returncode, 0)
            self.assertEqual(out, text)
            self.assertEqual(err, b'')

    def test_pipe(self):
        cat = popen(['cat', get_test_file()])
        process = popen(BINARY, stdin = cat)

        (out, err) = process.communicate()
        (cat_out, cat_err) = cat.communicate()

        self.assertEqual(cat.returncode, 0)
        self.assertEqual(process.returncode, 0)

        self.assertEqual(cat_err, b'')
        self.assertEqual(cat_out, b'')

        with open(get_test_file(), 'rb') as f:
            self.assertEqual(out, f.read())

if __name__ == '__main__':
    unittest.main(verbosity = 2)
