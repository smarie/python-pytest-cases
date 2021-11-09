# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize_with_cases


def case_sum_one_plus_two():
    a = 1
    b = 2
    c = 3
    return a, b, c


@parametrize_with_cases(argnames=["a", "b", "c"], cases=".")
def test_argnames_as_list(a, b, c):
    assert a + b == c


@parametrize_with_cases(argnames=("a", "b", "c"), cases=".")
def test_argnames_as_tuple(a, b, c):
    assert a + b == c


def test_argnames_from_invalid_type():
    with pytest.raises(
            TypeError, match="^argnames should be a string, list or a tuple$"
    ):
        parametrize_with_cases(argnames=42, cases=".")(lambda _: None)


def test_argnames_element_from_invalid_type():
    with pytest.raises(
            TypeError, match="^all argnames should be strings$"
    ):
        parametrize_with_cases(argnames=["a", 2, "c"], cases=".")(lambda _: None)
