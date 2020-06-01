import pytest
from pytest_cases import unpack_fixture, pytest_fixture_plus


@pytest_fixture_plus
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    return o, o[0]


a, b = unpack_fixture("a,b", c)


def test_function(a, b):
    assert a[0] == b


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_function[hello]',
                                        'test_function[world]']
