# test.py
import pytest
from pytest_cases import fixture_ref, pytest_parametrize_plus


@pytest.fixture
def foo():
    return 1


@pytest.fixture
def bar():
    return 2


@pytest_parametrize_plus("arg", [fixture_ref("foo"), fixture_ref("bar")])
def test_thing(arg):
    print(arg)


class TestCase:
    @pytest.mark.parametrize("arg", [1, 2])
    def test_thing_pytest(self, arg):
        print(arg)

    @pytest_parametrize_plus("arg", [fixture_ref("foo"), fixture_ref("bar")])
    def test_thing_cases(self, arg):
        print(arg)
