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
@pytest.mark.parametrize('foo', ['foo'])
def test_foo(arg, foo):
    assert foo == 'foo'
    assert arg in ['z',
                   'a',
                   'ba',
                   'bo',
                   'o']


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_foo[test_foo_param__arg__0-z-foo]',
                                        'test_foo[a-foo]',
                                        'test_foo[b-a-foo]',
                                        'test_foo[b-b_param__second_letter__1-o-foo]',
                                        'test_foo[test_foo_param__arg__3-o-foo]']
