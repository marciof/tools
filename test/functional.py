#!/usr/bin/env python3

import os
import subprocess
import unittest


BINARY = './show'


def popen(args, stdout = subprocess.PIPE, stdin = None):
    process = subprocess.Popen(args,
        stdin = stdin,
        stdout = stdout,
        stderr = subprocess.PIPE)

    return (process,) + process.communicate()


class TestPipePlugin (unittest.TestCase):

    def test_directory(self):
        path = '/'
        path_fd = os.open(path, os.O_RDONLY)

        try:
            (process, stdout, stderr) = popen([BINARY], stdin = path_fd)
            (ls, ls_stdout, ls_stderr) = popen(['ls', path])

            self.assertEqual(process.returncode, 0)
            self.assertEqual(stderr, b'')

            self.assertEqual(stdout, ls_stdout)
            self.assertEqual(stderr, ls_stderr)
            self.assertEqual(process.returncode, ls.returncode)
        finally:
            os.close(path_fd)


    def test_file(self):
        with open(__file__, 'rb') as f:
            text = f.read()
            f.seek(0)

            (process, stdout, stderr) = popen([BINARY], stdin=f)

            self.assertEqual(process.returncode, 0)
            self.assertEqual(stdout, text)
            self.assertEqual(stderr, b'')


if __name__ == '__main__':
    unittest.main()
