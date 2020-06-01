from distutils.version import LooseVersion

import pytest
from pytest_cases import fixture_union


@pytest.fixture
def a():
    return 1


u = fixture_union("u", (a, a))


def test_foo(u):
    pass


def test_synthesis(module_results_dct):
    if LooseVersion(pytest.__version__) < LooseVersion('3.0.0'):
        # the way to make ids uniques in case of duplicates was different in old pytest
        assert list(module_results_dct) == ['test_foo[0u_is_a]', 'test_foo[1u_is_a]']
    else:
        assert list(module_results_dct) == ['test_foo[u_is_a0]', 'test_foo[u_is_a1]']
