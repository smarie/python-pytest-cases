# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases


def a_case(monkeypatch):
    return True


def b_case(request):
    return True


@parametrize_with_cases("a", cases=".", prefix="a_")
@parametrize_with_cases("b", cases=".", prefix="b_")
def test_something(a, b):
    pass
