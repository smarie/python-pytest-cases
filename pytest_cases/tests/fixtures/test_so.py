import pytest

from pytest_cases import fixture_union, pytest_fixture_plus, NOT_USED


@pytest_fixture_plus(params=[1, 2, 3])
def lower(request):
    return "i" * request.param


@pytest.fixture(params=[1, 2])
def upper(request):
    # this fixture does not use pytest_fixture_plus so we have to explicitly discard the 'not used' cases
    if request.param is not NOT_USED:
        return "I" * request.param


fixture_union('all', ['lower', 'upper'])


def test_all(all):
    print(all)
