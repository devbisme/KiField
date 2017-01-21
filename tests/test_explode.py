#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_explode
----------------------------------

Tests for `kifield.explode` `kifield.collapse` functions.
"""

import unittest
import hypothesis
import hypothesis.strategies as st

from kifield import kifield


class TestExplode(unittest.TestCase):
    def test_works(self):
        refs = kifield.explode('C3, C2, C1')
        self.assertEqual(refs, ['C3', 'C2', 'C1'])

    def test_reversible(self):
        refs = kifield.explode('C1, C2, C3')
        self.assertEqual(refs, ['C1', 'C2', 'C3'])

    def test_no_spaces(self):
        refs = kifield.explode('C1,C2,C3')
        self.assertEqual(refs, ['C1', 'C2', 'C3'])

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

    def test_empty(self):
        refs = kifield.explode('')
        self.assertEqual(refs, [])


@st.composite
def random_references(draw):
    '''generates random lists of references like ['IASDHAH1', 'AKJDJAD1569', ...]'''
    #max_codepoint was derived empirically
    prefix = st.characters(blacklist_characters='0123456789,;-:', max_codepoint=1631)
    prefix = prefix.filter(lambda x: x.rstrip() != '')
    number = st.integers(min_value = 0)
    parts = draw(st.lists(st.tuples(prefix, number)))
    parts.sort()
    return list(map(lambda t: '{}{}'.format(t[0],t[1]), parts))


class TestCollapse(unittest.TestCase):
    def test_collapses(self):
        collapsed = kifield.collapse(['C1','C2','C3', 'C4'])
        self.assertEqual(collapsed, 'C1-C4')

    def test_collapses2(self):
        collapsed = kifield.collapse(['C1','C2','C3', 'C4', 'C6'])
        self.assertEqual(collapsed, 'C1-C4, C6')

    def test_collapses3(self):
        collapsed = kifield.collapse(['C1','C3', 'C4', 'C6'])
        self.assertEqual(collapsed, 'C1, C3, C4, C6')

    def test_collapses3(self):
        collapsed = kifield.collapse([])
        self.assertEqual(collapsed, '')

    @hypothesis.given(random_references())
    @hypothesis.settings(max_examples=1000)
    def test_explode_is_inverse(self, parts):
        assert kifield.explode(kifield.collapse(parts)) == parts

    @hypothesis.given(random_references())
    @hypothesis.settings(max_examples=1000)
    def test_explode_is_inverse2(self, references):
        assert kifield.collapse(kifield.explode(kifield.collapse(references))) == kifield.collapse(references)


