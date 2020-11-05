# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import parametrize_plus, fixture_plus, fixture_ref, lazy_value


@pytest.fixture
def world_str():
    """
    Èi̇·åıĸçºçº¿¿

    Args:
    """
    return 'world'


def whatfun():
    """
    Return the function that will be used as a function.

    Args:
    """
    return 'what'


@fixture_plus
@parametrize_plus('who', [fixture_ref(world_str),
                                 'you'])
def greetings(who):
    """
    Returns a string.

    Args:
        who: (todo): write your description
    """
    return 'hello ' + who


@parametrize_plus('main_msg', ['nothing',
                               fixture_ref(world_str),
                               lazy_value(whatfun),
                               fixture_ref(greetings)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    """
    Test if the main test.

    Args:
        main_msg: (str): write your description
        ending: (str): write your description
    """
    print(main_msg + ending)
