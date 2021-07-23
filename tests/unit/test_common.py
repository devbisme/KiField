from kifield.common import explode, collapse


def test_explode_works():
    refs = explode("C3, C2, C1")
    assert refs == ["C3", "C2", "C1"]


def test_explode_reversible():
    refs = explode("C1, C2, C3")
    assert refs == ["C1", "C2", "C3"]


def test_explode_no_spaces():
    refs = explode("C1,C2,C3")
    assert refs == ["C1", "C2", "C3"]


def test_explode_range():
    refs = explode("C1-C3")
    assert refs == ["C1", "C2", "C3"]


def test_explode_range2():
    refs = explode("C1-C3,C5")
    assert refs == ["C1", "C2", "C3", "C5"]


def test_explode_range_in_middle():
    refs = explode("C8,C1-C3,C5")
    assert refs == ["C8", "C1", "C2", "C3", "C5"]


def test_explode_range_colon():
    refs = explode("C1:C3,C5")
    assert refs == ["C1", "C2", "C3", "C5"]


def test_explode_range_with_spaces():
    refs = explode("C1 - C3")
    assert refs == ["C1", "C2", "C3"]


def test_explode_range_with_spaces2():
    refs = explode("C1 - C3,C4")
    assert refs == ["C1", "C2", "C3", "C4"]


def test_explode_range_with_spaces3():
    refs = explode("C1 - C3 , C4")
    assert refs == ["C1", "C2", "C3", "C4"]


def test_explode_range_with_spaces4():
    refs = explode("C1, C2 :C4")
    assert refs == ["C1", "C2", "C3", "C4"]


def test_explode_empty():
    refs = explode("")
    assert refs == []


def test_collapse_single():
    collapsed = collapse(["C1", "C2", "C3", "C4"])
    assert collapsed == "C1-C4"


def test_collapse_multiple():
    collapsed = collapse(["C1", "C2", "C3", "C4", "C8", "C9", "C10"])
    assert collapsed == "C1-C4, C8-C10"


def test_collapse_single_individual():
    collapsed = collapse(["C1", "C2", "C3", "C4", "C6"])
    assert collapsed == "C1-C4, C6"


def test_collapse_multiple_individual():
    collapsed = collapse(["C1", "C2", "C3", "C4", "C6", "C8", "C9", "C10"])
    assert collapsed == "C1-C4, C6, C8-C10"


def test_collapse_individuals():
    collapsed = collapse(["C1", "C3", "C4", "C6"])
    assert collapsed == "C1, C3, C4, C6"


def test_collapse_empty():
    collapsed = collapse([])
    assert collapsed == ""


# def toRef(part):
#     return "{}{}".format(part[0], part[1])


# @st.composite
# def random_prefix(draw):
#     # limited to unicode letters, see
#     # https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
#     categories = ["Ll", "Lt", "Lm", "Lo"]
#     characters = st.lists(st.characters(whitelist_categories=categories), min_size=1)
#     prefix = st.text(alphabet=draw(characters), min_size=1)
#     return draw(prefix)


# @st.composite
# def random_reference(draw, prefix=random_prefix()):
#     number = st.integers(min_value=0)
#     return draw(st.tuples(prefix, number))


# @st.composite
# def totally_random_references(draw):
#     """generates random sorted lists of references like ['IASDHAH1', 'ZKJDJAD1569', ...]"""
#     parts = draw(st.lists(random_reference()))
#     parts.sort()
#     return list(map(toRef, parts))


# @st.composite
# def random_references(draw):
#     """generates random sorted lists of references with the same prefix like ['IASDHAH1', 'IASDHAH1569', ...]"""
#     prefix = st.just(draw(random_prefix()))
#     parts = draw(st.lists(random_reference(prefix=prefix)))
#     parts.sort()
#     return list(map(toRef, parts))

# with settings:

#     class TestExplodeCollapseProperties(unittest.TestCase):
#         @hypothesis.given(random_references())
#         def test_explode_is_inverse(self, references):
#             assert explode(collapse(references)) == references

#         @hypothesis.given(random_references())
#         def test_explode_is_inverse2(self, references):
#             assert collapse(
#                 explode(collapse(references))
#             ) == collapse(references)

#         @hypothesis.given(totally_random_references())
#         def test_explode_is_inverse3(self, references):
#             assert explode(collapse(references)) == references

#         @hypothesis.given(totally_random_references())
#         def test_explode_is_inverse4(self, references):
#             assert collapse(
#                 explode(collapse(references))
#             ) == collapse(references)
