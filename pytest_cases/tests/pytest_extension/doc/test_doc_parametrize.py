import pytest
from pytest_cases import parametrize_plus, fixture_plus, fixture_ref, lazy_value


@pytest.fixture
def world_str():
    return 'world'


def whatfun():
    return 'what'


@fixture_plus
@parametrize_plus('who', [fixture_ref(world_str),
                                 'you'])
def greetings(who):
    return 'hello ' + who


@parametrize_plus('main_msg', ['nothing',
                               fixture_ref(world_str),
                               lazy_value(whatfun),
                               fixture_ref(greetings)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)
