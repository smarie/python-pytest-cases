import pytest

from pytest_cases import pytest_parametrize_plus, pytest_fixture_plus, fixture_ref


@pytest.fixture
def a():
    return 'a'


@pytest_fixture_plus
@pytest_parametrize_plus('second_letter', [fixture_ref('a'),
                                           'o'])
def b(second_letter):
    # second_letter = 'a'
    return 'b' + second_letter


@pytest_parametrize_plus('arg', ['z',
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
    assert list(module_results_dct) == ['test_foo[arg_is_z-bar]',
                                        'test_foo[arg_is_a-bar]',
                                        'test_foo[arg_is_b-second_letter_is_a-bar]',
                                        'test_foo[arg_is_b-second_letter_is_o-bar]',
                                        'test_foo[arg_is_o-bar]']
