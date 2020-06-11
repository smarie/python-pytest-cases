import pytest
from pytest_cases import pytest_parametrize_plus, pytest_fixture_plus, fixture_ref, parametrize_plus
from pytest_cases.tests.conftest import global_fixture


@pytest.fixture
def world_str():
    return 'world'


@pytest_fixture_plus
@pytest_parametrize_plus('who', [fixture_ref(world_str), 'you'])
def greetings(who):
    return 'hello ' + who


@pytest_parametrize_plus('main_msg', ['nothing', fixture_ref(world_str), fixture_ref(greetings),
                                      fixture_ref(global_fixture)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)


def test_synthesis(module_results_dct):
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
    return 3, 2


@parametrize_plus("a,b", [fixture_ref(c)])
def test_foo(a, b):
    """here the fixture is used for both parameters at the same time"""
    assert (a, b) == (3, 2)
