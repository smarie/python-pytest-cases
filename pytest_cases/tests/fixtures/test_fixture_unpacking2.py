import pytest
from pytest_cases import pytest_fixture_plus


@pytest_fixture_plus(unpack_into="a,b")
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    return o, o[0]


def test_function(a, b):
    assert a[0] == b


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_function[hello]',
                                        'test_function[world]']
