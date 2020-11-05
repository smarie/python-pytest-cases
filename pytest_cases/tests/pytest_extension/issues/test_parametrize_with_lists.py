# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import pytest_fixture_plus


@pytest_fixture_plus
@pytest.mark.parametrize(['c', 'd'], [(0, 0), (1, 1)])
def f(c, d):
    """
    R f ( a function )

    Args:
        c: (int): write your description
        d: (int): write your description
    """
    pass


@pytest.mark.parametrize(['a', 'b'], [(0, 0), (1, 1)])
def test_dummy(a, b, f):
    """
    Test if a is a b.

    Args:
        a: (todo): write your description
        b: (todo): write your description
        f: (todo): write your description
    """
    pass


def test_synthesis(module_results_dct):
    """
    Test if a module_results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ["test_dummy[0-0-0-0]",
                                        "test_dummy[0-0-1-1]",
                                        "test_dummy[1-1-0-0]",
                                        "test_dummy[1-1-1-1]"]
