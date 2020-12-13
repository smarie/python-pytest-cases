# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import fixture


@fixture
@pytest.mark.parametrize(['c', 'd'], [(0, 0), (1, 1)])
def f(c, d):
    pass


@pytest.mark.parametrize(['a', 'b'], [(0, 0), (1, 1)])
def test_dummy(a, b, f):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_dummy[0-0-0-0]",
                                        "test_dummy[0-0-1-1]",
                                        "test_dummy[1-1-0-0]",
                                        "test_dummy[1-1-1-1]"]
