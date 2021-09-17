# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize, fixture, fixture_ref


@pytest.fixture
def a():
    return 'A', 'AA'


@fixture
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


@parametrize("arg1,arg2", argvalues, idstyle='explicit')
def test_foo_explicit(arg1, arg2):
    print(arg1, arg2)


@parametrize("arg1,arg2", argvalues, idstyle='compact')
def test_foo_compact(arg1, arg2):
    print(arg1, arg2)


@parametrize("arg1,arg2", argvalues)  #default: idstyle=None
def test_foo_nostyle(arg1, arg2):
    print(arg1, arg2)


def test_synthesis(module_results_dct):
    """See https://github.com/smarie/python-pytest-cases/issues/86"""
    assert list(module_results_dct) == [
        # explicit
        'test_foo_explicit[(arg1,arg2)/P0:2-1-None]',
        'test_foo_explicit[(arg1,arg2)/P0:2-None-2]',
        'test_foo_explicit[(arg1,arg2)/a]',
        'test_foo_explicit[(arg1,arg2)/aaa]',  # <-- note that the custom id is used only in place of the fixture name
        'test_foo_explicit[(arg1,arg2)/4-4]',
        'test_foo_explicit[(arg1,arg2)/1-a]',
        'test_foo_explicit[(arg1,arg2)/3-b-1]',
        'test_foo_explicit[(arg1,arg2)/3-b-2]',
        # compact
        'test_foo_compact[/P0:2-1-None]',
        'test_foo_compact[/P0:2-None-2]',
        'test_foo_compact[/a]',
        'test_foo_compact[/aaa]',  # <-- note that the custom id is used only in place of the fixture name
        'test_foo_compact[/4-4]',
        'test_foo_compact[/1-a]',
        'test_foo_compact[/3-b-1]',
        'test_foo_compact[/3-b-2]',
        # no style
        'test_foo_nostyle[1-None]',
        'test_foo_nostyle[None-2]',
        'test_foo_nostyle[a]',
        'test_foo_nostyle[aaa]',
        'test_foo_nostyle[4-4]',
        'test_foo_nostyle[1-a]',
        'test_foo_nostyle[3-b-1]',
        'test_foo_nostyle[3-b-2]'
    ]
