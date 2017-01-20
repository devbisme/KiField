#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_kifield
----------------------------------

Tests for `kifield` module.
"""

import unittest

from kifield import kifield


class TestKifield(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        pass

    def tearDown(self):
        pass

class TestExplode(unittest.TestCase):
    def setUp(self):
        pass

    def test_works(self):
        refs = kifield.explode('C3, C2, C1')
        self.assertEqual(refs, ['C3', 'C2', 'C1'])
        pass

    def test_reversible(self):
        refs = kifield.explode('C1, C2, C3')
        self.assertEqual(refs, ['C1', 'C2', 'C3'])
        pass

    def test_nospaces(self):
        refs = kifield.explode('C1,C2,C3')
        self.assertEqual(refs, ['C1', 'C2', 'C3'])
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
