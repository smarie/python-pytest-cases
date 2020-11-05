# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases, fixture


@parametrize_with_cases("v")
def test(v):
    """
    Returns true if the test

    Args:
        v: (int): write your description
    """
    assert v == "one_proud_bird"


@fixture
def bird():
    """
    Returns the ] list ]

    Args:
    """
    return "one_proud_bird"
