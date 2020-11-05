# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import pytest_fixture_plus, fixture_union


state = -1


@pytest_fixture_plus
def a(request):
    """
    A context manager for the state of the state.

    Args:
        request: (todo): write your description
    """
    global state
    assert state == 3
    state = 0
    yield
    state = 1


@pytest_fixture_plus
def b(request):
    """
    A context manager that yields a context manager.

    Args:
        request: (todo): write your description
    """
    global state
    state = 2
    yield
    state = 3


c = fixture_union('c', [b, a])

# @pytest_fixture_plus
# def c(b, a):
#     pass


def test_all(c):
    """
    Test if c is_all

    Args:
        c: (todo): write your description
    """
    pass


def test_synthesis():
    """
    Test if a test.

    Args:
    """
    assert state == 1
