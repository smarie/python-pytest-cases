# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize, pytest_fixture_plus, fixture_ref


@pytest.fixture
def a():
    return 'A', 'AA'


@pytest_fixture_plus
@pytest.mark.parametrize('arg', [1, 2])
def b(arg):
    return "B%s" % arg


argvalues = [
    ('1', None),
    (None, '2'),
    fixture_ref('a'),
    fixture_ref('a', id="aaa"),
    ('4', '4'),
    ('1', fixture_ref('a')),
    ('3', fixture_ref('b'))
]


@parametrize("arg1,arg2", argvalues)
def test_foo(arg1, arg2):
    print(arg1, arg2)


@parametrize("arg1,arg2", argvalues, idstyle='compact')
def test_foo_compact(arg1, arg2):
    print(arg1, arg2)


@parametrize("arg1,arg2", argvalues, idstyle=None)
def test_foo_nostyle(arg1, arg2):
    print(arg1, arg2)


def test_synthesis(module_results_dct):
    """See https://github.com/smarie/python-pytest-cases/issues/86"""
    assert list(module_results_dct) == [
        'test_foo[arg1_arg2_is_P0toP1-1-None]',
        'test_foo[arg1_arg2_is_P0toP1-None-2]',
        'test_foo[arg1_arg2_is_a]',
        'test_foo[arg1_arg2_is_aaa]',
        'test_foo[arg1_arg2_is_4-4]',
        'test_foo[arg1_arg2_is_P5-1]',
        'test_foo[arg1_arg2_is_P5-2]'
    ]
