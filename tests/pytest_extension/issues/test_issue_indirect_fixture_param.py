# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest


@pytest.fixture
def my_fixture(request):
    return request.param


@pytest.fixture
def dependent_fixture(my_fixture):
    return my_fixture * 2


@pytest.mark.parametrize('my_fixture', [123], indirect=True)
def test_x(dependent_fixture):
    assert dependent_fixture == 2 * 123

