# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import parametrize, fixture, fixture_ref, lazy_value


@pytest.fixture
def world_str():
    return 'world'


def whatfun():
    return 'what'


@fixture
@parametrize('who', [world_str, 'you'])
def greetings(who):
    return 'hello ' + who


@parametrize('main_msg', ['nothing',
                          fixture_ref(world_str),
                          lazy_value(whatfun),
                          "1",
                          fixture_ref(greetings)],
             auto_refs=False)
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_prints[nothing-?]',
        'test_prints[nothing-!]',
        'test_prints[world_str-?]',
        'test_prints[world_str-!]',
        'test_prints[whatfun-?]',
        'test_prints[whatfun-!]',
        'test_prints[1-?]',
        'test_prints[1-!]',
        'test_prints[greetings-world_str-?]',
        'test_prints[greetings-world_str-!]',
        'test_prints[greetings-you-?]',
        'test_prints[greetings-you-!]'
    ]
