import pytest
from pytest_cases import fixture_union


@pytest.fixture
def a():
    return 1


u = fixture_union("u", (a, a))


def test_foo(u):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_foo[u_is_a0]', 'test_foo[u_is_a1]']
