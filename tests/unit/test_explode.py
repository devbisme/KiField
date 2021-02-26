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
        refs = kifield.explode("C3, C2, C1")
        self.assertEqual(refs, ["C3", "C2", "C1"])

    def test_reversible(self):
        refs = kifield.explode("C1, C2, C3")
        self.assertEqual(refs, ["C1", "C2", "C3"])

    def test_no_spaces(self):
        refs = kifield.explode("C1,C2,C3")
        self.assertEqual(refs, ["C1", "C2", "C3"])

    def test_range(self):
        refs = kifield.explode("C1-C3")
        self.assertEqual(refs, ["C1", "C2", "C3"])

    def test_range2(self):
        refs = kifield.explode("C1-C3,C5")
        self.assertEqual(refs, ["C1", "C2", "C3", "C5"])

    def test_range_in_middle(self):
        refs = kifield.explode("C8,C1-C3,C5")
        self.assertEqual(refs, ["C8", "C1", "C2", "C3", "C5"])

    def test_range_colon(self):
        refs = kifield.explode("C1:C3,C5")
        self.assertEqual(refs, ["C1", "C2", "C3", "C5"])

    def test_range_with_spaces(self):
        refs = kifield.explode("C1 - C3")
        self.assertEqual(refs, ["C1", "C2", "C3"])

    def test_range_with_spaces2(self):
        refs = kifield.explode("C1 - C3,C4")
        self.assertEqual(refs, ["C1", "C2", "C3", "C4"])

    def test_range_with_spaces3(self):
        refs = kifield.explode("C1 - C3 , C4")
        self.assertEqual(refs, ["C1", "C2", "C3", "C4"])

    def test_range_with_spaces4(self):
        refs = kifield.explode("C1, C2 :C4")
        self.assertEqual(refs, ["C1", "C2", "C3", "C4"])

    def test_empty(self):
        refs = kifield.explode("")
        self.assertEqual(refs, [])


class TestCollapse(unittest.TestCase):
    def test_collapses(self):
        collapsed = kifield.collapse(["C1", "C2", "C3", "C4"])
        self.assertEqual(collapsed, "C1-C4")

    def test_collapses2(self):
        collapsed = kifield.collapse(["C1", "C2", "C3", "C4", "C6"])
        self.assertEqual(collapsed, "C1-C4, C6")

    def test_collapses3(self):
        collapsed = kifield.collapse(["C1", "C3", "C4", "C6"])
        self.assertEqual(collapsed, "C1, C3, C4, C6")

    def test_empty(self):
        collapsed = kifield.collapse([])
        self.assertEqual(collapsed, "")


def toRef(part):
    return "{}{}".format(part[0], part[1])


@st.composite
def random_prefix(draw):
    # limited to unicode letters, see
    # https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
    categories = ["Ll", "Lt", "Lm", "Lo"]
    characters = st.lists(st.characters(whitelist_categories=categories), min_size=1)
    prefix = st.text(alphabet=draw(characters), min_size=1)
    return draw(prefix)


@st.composite
def random_reference(draw, prefix=random_prefix()):
    number = st.integers(min_value=0)
    return draw(st.tuples(prefix, number))


@st.composite
def totally_random_references(draw):
    """generates random sorted lists of references like ['IASDHAH1', 'ZKJDJAD1569', ...]"""
    parts = draw(st.lists(random_reference()))
    parts.sort()
    return list(map(toRef, parts))


@st.composite
def random_references(draw):
    """generates random sorted lists of references with the same prefix like ['IASDHAH1', 'IASDHAH1569', ...]"""
    prefix = st.just(draw(random_prefix()))
    parts = draw(st.lists(random_reference(prefix=prefix)))
    parts.sort()
    return list(map(toRef, parts))


settings = hypothesis.settings(
    max_examples=200,
    # generation may run slow on travis so we disable it
    # TODO make a profile for travis
    suppress_health_check=[hypothesis.HealthCheck.too_slow],
)

with settings:

    class TestExplodeCollapseProperties(unittest.TestCase):
        @hypothesis.given(random_references())
        def test_explode_is_inverse(self, references):
            assert kifield.explode(kifield.collapse(references)) == references

        @hypothesis.given(random_references())
        def test_explode_is_inverse2(self, references):
            assert kifield.collapse(
                kifield.explode(kifield.collapse(references))
            ) == kifield.collapse(references)

        @hypothesis.given(totally_random_references())
        def test_explode_is_inverse3(self, references):
            assert kifield.explode(kifield.collapse(references)) == references

        @hypothesis.given(totally_random_references())
        def test_explode_is_inverse4(self, references):
            assert kifield.collapse(
                kifield.explode(kifield.collapse(references))
            ) == kifield.collapse(references)
