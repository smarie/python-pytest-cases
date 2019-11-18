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

