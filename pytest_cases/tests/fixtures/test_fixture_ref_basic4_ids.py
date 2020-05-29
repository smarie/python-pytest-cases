import pytest

from pytest_cases import parametrize_plus, pytest_fixture_plus, fixture_ref


@pytest.fixture
def a():
    return 'A', 'AA'


@pytest_fixture_plus
@pytest.mark.parametrize('arg', [1, 2])
def b(arg):
    return "B%s" % arg


@parametrize_plus("arg1,arg2", [('1', None),
                                (None, '2'),
                                fixture_ref('a'),
                                ('4', '4'),
                                ('3', fixture_ref('b'))
                                ])
def test_foo(arg1, arg2):
    print(arg1, arg2)


def test_synthesis(module_results_dct):
    """See https://github.com/smarie/python-pytest-cases/issues/86"""
    assert list(module_results_dct) == [
        'test_foo[arg1_arg2_is_P0toP1-1-None]',
        'test_foo[arg1_arg2_is_P0toP1-None-2]',
        'test_foo[arg1_arg2_is_a]',
        'test_foo[arg1_arg2_is_4-4]',
        'test_foo[arg1_arg2_is_P4-1]',
        'test_foo[arg1_arg2_is_P4-2]'
    ]
