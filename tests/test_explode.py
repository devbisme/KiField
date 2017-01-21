#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_explode
----------------------------------

Tests for `kifield.explode` function.
"""

import unittest

from kifield import kifield


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

    def test_no_spaces(self):
        refs = kifield.explode('C1,C2,C3')
        self.assertEqual(refs, ['C1', 'C2', 'C3'])
        pass

    def test_range(self):
        refs = kifield.explode('C1-C3')
        self.assertEqual(refs, ['C1','C2','C3'])

    def test_range2(self):
        refs = kifield.explode('C1-C3,C5')
        self.assertEqual(refs, ['C1','C2','C3', 'C5'])

    def test_range_in_middle(self):
        refs = kifield.explode('C8,C1-C3,C5')
        self.assertEqual(refs, ['C8', 'C1','C2','C3', 'C5'])

    def test_range_colon(self):
        refs = kifield.explode('C1:C3,C5')
        self.assertEqual(refs, ['C1','C2','C3', 'C5'])

    def test_range_with_spaces(self):
        refs = kifield.explode('C1 - C3')
        self.assertEqual(refs, ['C1','C2','C3'])

    def test_range_with_spaces2(self):
        refs = kifield.explode('C1 - C3,C4')
        self.assertEqual(refs, ['C1','C2','C3', 'C4'])

    def test_range_with_spaces3(self):
        refs = kifield.explode('C1 - C3 , C4')
        self.assertEqual(refs, ['C1','C2','C3', 'C4'])

    def test_range_with_spaces4(self):
        refs = kifield.explode('C1, C2 :C4')
        self.assertEqual(refs, ['C1','C2','C3', 'C4'])

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
