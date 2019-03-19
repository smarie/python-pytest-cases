from pytest_cases import pytest_fixture_plus
import pytest


@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize("arg1", [
    "one", "two"
])
@pytest.mark.parametrize("arg2", [
    "one", "two"
])
def myfix(arg1, arg2):
    return (arg1, arg2)


def test_one(myfix):
    print(myfix)


@pytest_fixture_plus
@pytest.mark.parametrize("arg1, arg2", [
    (1, 2),
    (3, 4),
])
def myfix2(arg1, arg2):
    return arg1, arg2

def test_two(myfix2):
    print(myfix)
