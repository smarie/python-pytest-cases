import pytest
from pytest_cases import pytest_parametrize_plus, pytest_fixture_plus, fixture_ref


@pytest.fixture
def world_str():
    return 'world'


@pytest_fixture_plus
@pytest_parametrize_plus('who', [fixture_ref(world_str), 'you'])
def greetings(who):
    return 'hello ' + who


@pytest_parametrize_plus('main_msg', ['nothing', fixture_ref(world_str), fixture_ref(greetings)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_prints[test_prints_param__main_msg__0-nothing-?]',
                                        'test_prints[test_prints_param__main_msg__0-nothing-!]',
                                        'test_prints[world_str-?]',
                                        'test_prints[world_str-!]',
                                        'test_prints[greetings-world_str-?]',
                                        'test_prints[greetings-world_str-!]',
                                        'test_prints[greetings-greetings_param__who__1-you-?]',
                                        'test_prints[greetings-greetings_param__who__1-you-!]']
