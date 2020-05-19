"""
Copy of test_fixture_in_parametrize.py to test using of pytest.param for marking tests with id in parametrize_plus

Showcased bugs:
    * id is applied even on the second fixture if it doesnt override it (fixture_ref(a))
    * fixture_ref is not translated to an actual fixture value
"""
import pytest

from pytest_cases import fixture_ref, parametrize_plus, fixture_plus


@pytest.fixture
def a():
    return 'a'


@fixture_plus
@parametrize_plus('second_letter', [fixture_ref('a'),
                                    'o'])
def b(second_letter):
    # second_letter = 'a'
    return 'b' + second_letter


@parametrize_plus('arg', [pytest.param('z', id="id-z"),
                          fixture_ref(a),
                          pytest.param(fixture_ref(b), id="id-b"),
                          pytest.param('o', id="id-o")])
@pytest.mark.parametrize('bar', ['bar'])
def test_foo(arg, bar):
    assert bar == 'bar'
    assert arg in ['z',
                   'a',
                   'ba',
                   'bo',
                   'o']


def test_synthesis(module_results_dct):
    """This is the actual result
    ['test_foo[arg_is_0-id-z-id-b-bar]',
     'test_foo[arg_is_0-id-z-id-o-bar]',
     'test_foo[arg_is_a-id-z-id-b-bar]',
     'test_foo[arg_is_a-id-z-id-o-bar]',
     'test_foo[arg_is_2to3-id-z-id-b-bar]',
     'test_foo[arg_is_2to3-id-z-id-o-bar]']"""
    assert list(module_results_dct) == ['test_foo[arg_is_0-idz-bar]',
                                        'test_foo[arg_is_a-bar]',
                                        'test_foo[arg_is_b-second_letter_is_a-bar]',
                                        'test_foo[arg_is_b-second_letter_is_1-o-bar]',
                                        'test_foo[arg_is_3-o-bar]']
