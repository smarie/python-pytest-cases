# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases


def a_case(monkeypatch):
    """
    Returns true if a case is a case.

    Args:
        monkeypatch: (todo): write your description
    """
    return True


def b_case(request):
    """
    Return true if the request is a b - b.

    Args:
        request: (todo): write your description
    """
    return True


@parametrize_with_cases("a", cases=".", prefix="a_")
@parametrize_with_cases("b", cases=".", prefix="b_")
def test_something(a, b):
    """
    Test if a and b.

    Args:
        a: (todo): write your description
        b: (todo): write your description
    """
    pass
