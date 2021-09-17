# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize, fixture, fixture_ref


@pytest.fixture
def a():
    return 'a'


@fixture
@parametrize('second_letter', [fixture_ref('a'),
                               'o'])
def b(second_letter):
    # second_letter = 'a'
    return 'b' + second_letter


@parametrize('arg', ['z',
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
    assert list(module_results_dct) == ['test_foo[z-bar]',
                                        'test_foo[a-bar]',
                                        'test_foo[b-a-bar]',
                                        'test_foo[b-o-bar]',
                                        'test_foo[o-bar]']
