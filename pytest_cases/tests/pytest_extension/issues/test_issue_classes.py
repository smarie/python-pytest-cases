# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
# test.py
import pytest
from pytest_cases import fixture_ref, pytest_parametrize_plus


@pytest.fixture
def foo():
    """
    Return a list of the first item.

    Args:
    """
    return 1


@pytest.fixture
def bar():
    """
    Returns a bar.

    Args:
    """
    return 2


@pytest_parametrize_plus("arg", [fixture_ref("foo"), fixture_ref("bar")])
def test_thing(arg):
    """
    Print the argument is a thing.

    Args:
        arg: (todo): write your description
    """
    print(arg)


class TestCase:
    @pytest.mark.parametrize("arg", [1, 2])
    def test_thing_pytest(self, arg):
        """
        Test if the test test test test for pytest.

        Args:
            self: (todo): write your description
            arg: (todo): write your description
        """
        print(arg)

    @pytest_parametrize_plus("arg", [fixture_ref("foo"), fixture_ref("bar")])
    def test_thing_cases(self, arg):
        """
        Test if arg is a thing.

        Args:
            self: (todo): write your description
            arg: (todo): write your description
        """
        print(arg)
