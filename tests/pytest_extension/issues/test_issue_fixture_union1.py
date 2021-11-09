# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from distutils.version import LooseVersion

import pytest

from pytest_cases.common_pytest_marks import PYTEST3_OR_GREATER
from pytest_cases import fixture_union


@pytest.fixture
def a():
    return 1


u = fixture_union("u", (a, a))


def test_foo(u):
    pass


def test_synthesis(module_results_dct):
    if not PYTEST3_OR_GREATER:
        # the way to make ids uniques in case of duplicates was different in old pytest
        assert list(module_results_dct) == ['test_foo[0/a]', 'test_foo[1/a]']
    else:
        assert list(module_results_dct) == ['test_foo[/a0]', 'test_foo[/a1]']
