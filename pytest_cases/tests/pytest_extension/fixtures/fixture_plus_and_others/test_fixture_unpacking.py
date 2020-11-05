# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import unpack_fixture, pytest_fixture_plus


@pytest_fixture_plus
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    """
    Return the c : class

    Args:
        o: (int): write your description
    """
    return o, o[0]


a, b = unpack_fixture("a,b", c)


def test_function(a, b):
    """
    Test if a b.

    Args:
        a: (str): write your description
        b: (str): write your description
    """
    assert a[0] == b


def test_synthesis(module_results_dct):
    """
    Test if a module_results_dcthesis.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_function[hello]',
                                        'test_function[world]']
