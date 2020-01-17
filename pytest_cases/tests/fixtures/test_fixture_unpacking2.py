import pytest
from pytest_cases import fixture_plus, pytest_fixture_plus, fixture_union


@fixture_plus(unpack_into="a,b")
@pytest.mark.parametrize("o", ['hello', 'world'])
def root1(o):
    return o, o[0]


def test_function(a, b):
    assert a[0] == b
    assert a in ('hello', 'world')


@pytest_fixture_plus
@pytest.mark.parametrize("o", ['yeepee', 'yay'])
def root2(o):
    return o, o[0]


fixture_union("root", [root1, root2], unpack_into="c,d")


def test_function2(c, d):
    assert c[0] == d
    assert c in ('hello', 'world', 'yeepee', 'yay')


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_function[hello]',
                                        'test_function[world]',
                                        'test_function2[root_is_root1-hello]',
                                        'test_function2[root_is_root1-world]',
                                        'test_function2[root_is_root2-yeepee]',
                                        'test_function2[root_is_root2-yay]',
                                        ]
