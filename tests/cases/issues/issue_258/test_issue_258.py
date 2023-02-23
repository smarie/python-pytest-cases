from pytest_cases import (AUTO, case, get_all_cases, parametrize,
                          parametrize_with_cases)


@case(tags=["a", "banana"])
def case_1():
    return "a_banana"


@case(tags=["a"])
def case_2():
    return "a"


@case(tags=["b", "banana"])
def case_3():
    return "b_banana"


@case(tags=["b"])
def case_4():
    return "b"


all_cases = get_all_cases(cases=[case_1, case_2, case_3, case_4])
a_cases = get_all_cases(cases=all_cases, has_tag="a")
b_cases = get_all_cases(cases=all_cases, has_tag="b")
banana_cases = get_all_cases(cases=a_cases + b_cases, has_tag=["banana"])


# Test behaviour with explicit cases and no parametrization target
##################################################################
@parametrize_with_cases("word", cases=all_cases)
def test_all(word):
    assert word in ["a", "a_banana", "b", "b_banana"]


@parametrize_with_cases("word", cases=a_cases)
def test_a(word):
    assert "a" in word


@parametrize_with_cases("word", cases=b_cases)
def test_b(word):
    assert "b" in word


@parametrize_with_cases("word", cases=banana_cases)
def test_banana(word):
    assert "banana" in word


# Test behaviour with string module ref and AUTO and no parametrization target
##############################################################################
def test_this_module_cases():
    this_module_cases = get_all_cases(cases=".")
    assert set(this_module_cases) == {case_1, case_2, case_3, case_4}


def test_relative_module_cases():
    relative_import_cases = get_all_cases(cases=".cases")
    assert {"hello .", "hi ."} == {f() for f in relative_import_cases}


@parametrize("explicit", (True, False))
def test_auto_cases(explicit):
    if explicit:
        auto_import_cases = get_all_cases(cases=AUTO)
    else:
        auto_import_cases = get_all_cases()
    assert {"hello AUTO", "hi AUTO"} == {f() for f in auto_import_cases}


# Test behaviour with an explicit module parametrization target
###############################################################
from tests.cases.issues.issue_258 import test_other
def test_module_parametrization_auto():
    cases_other_cases = get_all_cases(test_other, cases=AUTO)
    assert {"hello cases_other", "hi cases_other"} == {f() for f in cases_other_cases}


def test_module_parametrization_this_module():
    test_other_cases = get_all_cases(test_other, cases='.')
    assert {"hello test_other", "hi test_other"} == {f() for f in test_other_cases}
