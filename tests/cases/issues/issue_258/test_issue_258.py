from pytest_cases import get_all_cases, case, parametrize_with_cases, parametrize
import pytest
from pytest_cases.case_parametrizer_new import AUTO


# Test behaviour without a string module ref
############################################

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


def test_get_cases_without_parametrization_target():
    assert len(list(all_cases)) == 4
    assert len(list(a_cases)) == 2
    assert len(list(b_cases)) == 2
    assert len(list(banana_cases)) == 2


@parametrize("ref", ['.'])
def test_get_all_cases_raises_with_module_case(ref):
    with pytest.raises(ValueError, match="Cases beginning with"):
        get_all_cases(cases=ref)


# Test behaviour with string module ref
#######################################
def test_relative_import_cases_is_none_empty():
    relative_import_cases = get_all_cases(cases=".cases")
    assert len(relative_import_cases) == 2


def test_auto_import_cases_is_non_empty():
    auto_import_cases = get_all_cases(cases=AUTO)
    assert len(auto_import_cases) == 2
