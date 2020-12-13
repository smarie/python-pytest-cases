# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import fixture, fixture_union


@fixture(unpack_into="a,b")
@pytest.mark.parametrize("o", ['hello', 'world'])
def root1(o):
    return o, o[0]


def test_function(a, b):
    assert a[0] == b
    assert a in ('hello', 'world')


@fixture
@pytest.mark.parametrize("o", ['yeepee', 'yay'])
def root2(o):
    return o, o[0]


fixture_union("root", [root1, root2], unpack_into="c,d")


def test_function2(c, d):
    assert c[0] == d
    assert c in ('hello', 'world', 'yeepee', 'yay')


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_function[hello]',
        'test_function[world]',
        'test_function2[/root1-hello]',
        'test_function2[/root1-world]',
        'test_function2[/root2-yeepee]',
        'test_function2[/root2-yay]',
    ]
