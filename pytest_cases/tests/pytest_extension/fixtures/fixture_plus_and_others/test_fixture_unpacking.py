# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import unpack_fixture, fixture


@fixture
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    return o, o[0]


a, b = unpack_fixture("a,b", c)


def test_function(a, b):
    assert a[0] == b


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_function[hello]',
                                        'test_function[world]']
