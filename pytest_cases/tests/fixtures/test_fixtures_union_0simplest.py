import pytest
from pytest_cases import fixture_union


@pytest.fixture
def first():
    return 'hello'


@pytest.fixture(params=['a', 'b'])
def second(request):
    return request.param


c = fixture_union('c', [first, second])


def test_basic_union(c):
    print(c)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_basic_union[c_is_first]",
                                        "test_basic_union[c_is_second-a]",
                                        "test_basic_union[c_is_second-b]"]
