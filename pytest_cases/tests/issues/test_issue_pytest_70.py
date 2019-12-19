import pytest
from pytest_cases import fixture_ref, pytest_parametrize_plus, pytest_fixture_plus


@pytest_fixture_plus
@pytest_parametrize_plus("variant", ['A', 'B'])
def book1(variant):
    return variant


@pytest.fixture
def book2():
    return


@pytest_parametrize_plus("name", [
    fixture_ref(book1),
    'hi',
    'ih',
    fixture_ref(book2),
])
def test_get_or_create_book(name):
    print(name)
