# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import fixture, fixture_ref, parametrize
from pytest_cases.tests.conftest import global_fixture


@pytest.fixture
def world_str():
    return 'world'


@fixture
@parametrize('who', [fixture_ref(world_str), 'you'])
def greetings(who):
    return 'hello ' + who


@parametrize('main_msg', ['nothing',
                          fixture_ref(world_str),
                          fixture_ref(greetings),
                          fixture_ref(global_fixture)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_prints[nothing-?]',
                                        'test_prints[nothing-!]',
                                        'test_prints[world_str-?]',
                                        'test_prints[world_str-!]',
                                        'test_prints[greetings-world_str-?]',
                                        'test_prints[greetings-world_str-!]',
                                        'test_prints[greetings-you-?]',
                                        'test_prints[greetings-you-!]',
                                        'test_prints[global_fixture-?]',
                                        'test_prints[global_fixture-!]']


@pytest.fixture
def c():
    return 3, 2


@parametrize("a,b", [fixture_ref(c)])
def test_foo(a, b):
    """here the fixture is used for both parameters at the same time"""
    assert (a, b) == (3, 2)
