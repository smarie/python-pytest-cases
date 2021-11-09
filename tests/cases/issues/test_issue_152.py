import pytest

from pytest_cases import fixture, parametrize_with_cases

used = False


@fixture
def validationOff():
    global used
    used = True
    yield
    used = False


def case_first(validationOff):
    pass


@pytest.mark.usefixtures("validationOff")
def case_second():
    pass


@parametrize_with_cases("a", cases='.')
def test_uses_fixture(a):
    global used
    assert used
