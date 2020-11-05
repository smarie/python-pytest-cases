# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import fixture_plus, pytest_fixture_plus, fixture_union


@fixture_plus(unpack_into="a,b")
@pytest.mark.parametrize("o", ['hello', 'world'])
def root1(o):
    """
    Return the root of o.

    Args:
        o: (todo): write your description
    """
    return o, o[0]


def test_function(a, b):
    """
    Test if two two b.

    Args:
        a: (str): write your description
        b: (str): write your description
    """
    assert a[0] == b
    assert a in ('hello', 'world')


@pytest_fixture_plus
@pytest.mark.parametrize("o", ['yeepee', 'yay'])
def root2(o):
    """
    Return the root of o.

    Args:
        o: (todo): write your description
    """
    return o, o[0]


fixture_union("root", [root1, root2], unpack_into="c,d")


def test_function2(c, d):
    """
    Test the test test.

    Args:
        c: (todo): write your description
        d: (todo): write your description
    """
    assert c[0] == d
    assert c in ('hello', 'world', 'yeepee', 'yay')


def test_synthesis(module_results_dct):
    """
    Test if the test results to test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_function[hello]',
                                        'test_function[world]',
                                        'test_function2[root_is_root1-hello]',
                                        'test_function2[root_is_root1-world]',
                                        'test_function2[root_is_root2-yeepee]',
                                        'test_function2[root_is_root2-yay]',
                                        ]
