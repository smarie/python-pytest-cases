#  Authors: Eddie Bergmane <eddiebergmanehs@gmail.com>
#            + All contributors to <https://github.com/smarie/python-pyfields>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-pyfields/blob/master/LICENSE>
#
#  Issue: https://github.com/smarie/python-pytest-cases/issues/258
from pytest_cases import get_all_cases, case, parametrize_with_cases


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
