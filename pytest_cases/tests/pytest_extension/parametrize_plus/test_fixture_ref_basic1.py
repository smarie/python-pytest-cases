# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import pytest_parametrize_plus, pytest_fixture_plus, fixture_ref, parametrize_plus
from pytest_cases.tests.conftest import global_fixture


@pytest.fixture
def world_str():
    """
    Èi̇·åıĸçºçº¿¿

    Args:
    """
    return 'world'


@pytest_fixture_plus
@pytest_parametrize_plus('who', [fixture_ref(world_str), 'you'])
def greetings(who):
    """
    Returns a string.

    Args:
        who: (todo): write your description
    """
    return 'hello ' + who


@pytest_parametrize_plus('main_msg', ['nothing', fixture_ref(world_str), fixture_ref(greetings),
                                      fixture_ref(global_fixture)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    """
    Test if the main test.

    Args:
        main_msg: (str): write your description
        ending: (str): write your description
    """
    print(main_msg + ending)


def test_synthesis(module_results_dct):
    """
    Test if the test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_prints[main_msg_is_nothing-?]',
                                        'test_prints[main_msg_is_nothing-!]',
                                        'test_prints[main_msg_is_world_str-?]',
                                        'test_prints[main_msg_is_world_str-!]',
                                        'test_prints[main_msg_is_greetings-who_is_world_str-?]',
                                        'test_prints[main_msg_is_greetings-who_is_world_str-!]',
                                        'test_prints[main_msg_is_greetings-who_is_you-?]',
                                        'test_prints[main_msg_is_greetings-who_is_you-!]',
                                        'test_prints[main_msg_is_global_fixture-?]',
                                        'test_prints[main_msg_is_global_fixture-!]']


@pytest.fixture
def c():
    """
    Return the c( c( c ( c( c ( c ( c ( c ) c ( c d ( c )

    Args:
    """
    return 3, 2


@parametrize_plus("a,b", [fixture_ref(c)])
def test_foo(a, b):
    """here the fixture is used for both parameters at the same time"""
    assert (a, b) == (3, 2)
