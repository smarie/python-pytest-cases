# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import warnings

import pytest

from pytest_cases.common_pytest_marks import PYTEST3_OR_GREATER
from pytest_cases import fixture_union


@pytest.fixture
def a():
    return 1


@pytest.fixture
def b():
    return 1


with warnings.catch_warnings():
    # ignore the warning about the two values being the same fixture.
    warnings.simplefilter("ignore")
    u = fixture_union("u", (a, b, a), ids=['1', '2', '3'])


def test_foo(u):
    pass


with warnings.catch_warnings():
    # ignore the warning about the two values being the same fixture.
    warnings.simplefilter("ignore")
    v = fixture_union("v", (a, b, a))


def test_foo2(v):
    pass


def test_synthesis(module_results_dct):
    if not PYTEST3_OR_GREATER:
        # the way to make ids uniques in case of duplicates was different in old pytest
        assert list(module_results_dct) == [
            'test_foo[1]',
            'test_foo[2]',
            'test_foo[3]',
            'test_foo2[0/a]',
            'test_foo2[1/b]',
            'test_foo2[2/a]'
        ]
    else:
        assert list(module_results_dct) == [
            'test_foo[1]',
            'test_foo[2]',
            'test_foo[3]',
            'test_foo2[/a0]',
            'test_foo2[/b]',
            'test_foo2[/a1]'
        ]
