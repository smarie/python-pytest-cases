"""
Simplified version of test_mark_param_in_parametrize.py to showcase how normal parametrize acts
"""
import pytest

from pytest_cases import fixture_ref, parametrize_plus, fixture_plus


@pytest.mark.parametrize('arg', [pytest.param('z', marks=pytest.mark.skipif("5>4")),
                                 'a',
                                 'b',
                                 pytest.param('o', marks=pytest.mark.skipif("4>5"))])
@pytest.mark.parametrize('bar', ['bar'])
def test_foo(arg, bar):
    assert bar == 'bar'
    assert arg in ['z',
                   'a',
                   'b',
                   'o']


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_foo[bar-a]', 'test_foo[bar-b]', 'test_foo[bar-o]']
