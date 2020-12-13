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
@parametrize('who', [fixture_ref(world_str),
                                 'you'])
def greetings(who):
    return 'hello ' + who


@parametrize('main_msg', ['nothing',
                               fixture_ref(world_str),
                               lazy_value(whatfun),
                               fixture_ref(greetings)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)
