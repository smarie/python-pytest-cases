# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
# test.py
import pytest
from pytest_cases import fixture_ref, parametrize


@pytest.fixture
def foo():
    return 1


@pytest.fixture
def bar():
    return 2


@parametrize("arg", [fixture_ref("foo"), fixture_ref("bar")])
def test_thing(arg):
    print(arg)


class TestCase:
    @pytest.mark.parametrize("arg", [1, 2])
    def test_thing_pytest(self, arg):
        print(arg)

    @parametrize("arg", [fixture_ref("foo"), fixture_ref("bar")])
    def test_thing_cases(self, arg):
        print(arg)
