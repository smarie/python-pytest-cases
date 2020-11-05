# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import parametrize, parametrize_with_cases


@parametrize(i=range(2), idgen="i=={i}")
def case_i(i):
    """
    Returns : class : class : i.

    Args:
        i: (todo): write your description
    """
    return i + 1


@pytest.mark.parametrize('i', range(2), ids="i=={}".format)
def case_k(i):
    """
    Case - 1d ( i - th integer ) of i.

    Args:
        i: (todo): write your description
    """
    return i + 1


@parametrize_with_cases(argnames="j", cases='.')
def test_me(j):
    """
    Return the current state of a j.

    Args:
        j: (array): write your description
    """
    assert j > 0


def test_synthesis(module_results_dct):
    """
    Test for test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == [
        'test_me[i-i==0]',
        'test_me[i-i==1]',
        'test_me[k-i==0]',
        'test_me[k-i==1]',
    ]
