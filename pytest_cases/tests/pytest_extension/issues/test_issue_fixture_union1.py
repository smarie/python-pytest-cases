# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from distutils.version import LooseVersion

import pytest
from pytest_cases import fixture_union


@pytest.fixture
def a():
    """
    Returns the first two - way function.

    Args:
    """
    return 1


u = fixture_union("u", (a, a))


def test_foo(u):
    """
    Test if the given python object

    Args:
        u: (todo): write your description
    """
    pass


def test_synthesis(module_results_dct):
    """
    Test for python 2.

    Args:
        module_results_dct: (todo): write your description
    """
    if LooseVersion(pytest.__version__) < LooseVersion('3.0.0'):
        # the way to make ids uniques in case of duplicates was different in old pytest
        assert list(module_results_dct) == ['test_foo[0u_is_a]', 'test_foo[1u_is_a]']
    else:
        assert list(module_results_dct) == ['test_foo[u_is_a0]', 'test_foo[u_is_a1]']
