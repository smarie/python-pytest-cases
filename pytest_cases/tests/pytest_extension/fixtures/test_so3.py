# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import fixture


@fixture(unpack_into="foo,bar")
def foobar():
    return "blah", "whatever"


def test_stuff(foo, bar):
    assert foo == "blah" and bar == "whatever"
