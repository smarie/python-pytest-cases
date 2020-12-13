# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import fixture, fixture_union


state = -1


@fixture
def a(request):
    global state
    assert state == 3
    state = 0
    yield
    state = 1


@fixture
def b(request):
    global state
    state = 2
    yield
    state = 3


c = fixture_union('c', [b, a])

# @fixture
# def c(b, a):
#     pass


def test_all(c):
    pass


def test_synthesis():
    assert state == 1
