import pytest

import pytest_cases
from pytest_cases.tests.utils import skip as skip_mark


@pytest.mark.parametrize('v', [0, skip_mark(1)])
def test_foo_simple_param(v):
    pass


@pytest.fixture(params=[0, skip_mark(1)])
def foo2(request):
    pass


def test_foo2_paramfix(foo2):
    pass


@pytest_cases.fixture
@pytest.mark.parametrize('v', [0, skip_mark(1)])
def foo3(request, v):
    pass


def test_foo3_paramfix(foo3):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_foo_simple_param[0]',
        'test_foo2_paramfix[0]',
        'test_foo3_paramfix[0]',
    ]
