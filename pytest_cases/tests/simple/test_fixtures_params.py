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

