# -*- coding: UTF-8 -*-


def exists(env):
    try:
        import unittest
        return hasattr(unittest.TestLoader, 'discover')
    except ImportError:
        return False


def generate(env):
    env.Append(BUILDERS = {'UnitTest':
        env.Builder(action = [['python', '-m', 'unittest', 'discover']])})
