# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest


@pytest.fixture
def my_fixture(request):
    """
    Return a request as a list.

    Args:
        request: (todo): write your description
    """
    return request.param


@pytest.fixture
def dependent_fixture(my_fixture):
    """
    Return a function that fixture fixture.

    Args:
        my_fixture: (str): write your description
    """
    return my_fixture * 2


@pytest.mark.parametrize('my_fixture', [123], indirect=True)
def test_x(dependent_fixture):
    """
    : parameter_fixture.

    Args:
        dependent_fixture: (str): write your description
    """
    assert dependent_fixture == 2 * 123

