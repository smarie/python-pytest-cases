"""
Copy of test_fixture_in_parametrize.py to test using of pytest.param for adding additional marks in parametrize_plus

Bugs:
   * Skipif is applied to all values even if should be applied to only the first case
   * Second skipif is ignored (maybe because of the first problem)
"""
import pytest

from pytest_cases import fixture_ref, parametrize_plus, fixture_plus


@pytest.fixture
def a():
    return 'a'


@fixture_plus
@parametrize_plus('second_letter', [fixture_ref('a'),
                                    pytest.param('o', marks=pytest.mark.skipif("4>5"))])
def b(second_letter):
    # second_letter = 'a'
    return 'b' + second_letter


@parametrize_plus('arg', [pytest.param('z', marks=pytest.mark.skipif("5>4")),
                          fixture_ref(a),
                          fixture_ref(b),
                          'o'])
@pytest.mark.parametrize('bar', ['bar'])
def test_foo(arg, bar):
    assert bar == 'bar'
    assert arg in ['z',
                   'a',
                   'ba',
                   'bo',
                   'o']


def test_synthesis(module_results_dct):
    """This is the actual result []"""
    assert list(module_results_dct) == ['test_foo[arg_is_0-idz-bar]',
                                        'test_foo[arg_is_a-bar]',
                                        'test_foo[arg_is_b-second_letter_is_a-bar]',
                                        'test_foo[arg_is_b-second_letter_is_1-o-bar]',
                                        'test_foo[arg_is_3-o-bar]']
