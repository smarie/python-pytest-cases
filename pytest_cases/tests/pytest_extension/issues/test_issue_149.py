import pytest

from pytest_cases.common_pytest_marks import PYTEST3_OR_GREATER
from pytest_cases import parametrize, lazy_value, fixture, is_lazy


def x():
    return []


@parametrize("y", [0, 1])
@parametrize("x", [lazy_value(x)])
@pytest.mark.skipif(not PYTEST3_OR_GREATER,
                    reason="request.getfixturevalue is not available in pytest 2")
def test_foo(x, y, my_cache_verifier):
    print(x, y)
    # make sure the cache works correctly: different requests trigger different calls
    assert x == ['added_by_fixture']
    x.append("added_by_test")


@fixture
def my_cache_verifier(request):
    x = request.getfixturevalue('x')
    assert is_lazy(x)
    x = x.get(request)
    x.append('added_by_fixture')
    yield
    x = request.getfixturevalue('x')
    assert is_lazy(x)
    x = x.get(request)
    assert x == ['added_by_fixture', "added_by_test"]
