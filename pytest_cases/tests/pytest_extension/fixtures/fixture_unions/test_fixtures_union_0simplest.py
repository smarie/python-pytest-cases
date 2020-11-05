# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import fixture_union


@pytest.fixture
def first():
    """
    Return first ]

    Args:
    """
    return 'hello'


@pytest.fixture(params=['a', 'b'])
def second(request):
    """
    Return a request.

    Args:
        request: (todo): write your description
    """
    return request.param


c = fixture_union('c', [first, second])


def test_basic_union(c):
    """
    Test if a union of the union of a union.

    Args:
        c: (todo): write your description
    """
    print(c)


def test_synthesis(module_results_dct):
    """
    Test for test_results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ["test_basic_union[c_is_first]",
                                        "test_basic_union[c_is_second-a]",
                                        "test_basic_union[c_is_second-b]"]
