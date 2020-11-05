# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import pytest_fixture_plus


@pytest_fixture_plus(unpack_into="foo,bar")
def foobar():
    """
    Èi̇·åıĸçńķæł¥¨

    Args:
    """
    return "blah", "whatever"


def test_stuff(foo, bar):
    """
    Taobao.

    Args:
        foo: (todo): write your description
        bar: (todo): write your description
    """
    assert foo == "blah" and bar == "whatever"
