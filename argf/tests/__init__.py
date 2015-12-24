# -*- coding: UTF-8 -*-


"""
Compatibility layer.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals


try:
    # External:
    import unittest2 as unittest
except ImportError:
    # Standard:
    import unittest


if hasattr(unittest.TestCase, 'assertRaisesRegex'):
    TestCase = unittest.TestCase
else:
    class TestCase (unittest.TestCase):
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp
