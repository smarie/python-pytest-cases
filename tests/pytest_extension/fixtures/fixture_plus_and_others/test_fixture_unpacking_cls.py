import pytest

from pytest_cases import fixture, unpack_fixture


@fixture
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    return o, o[0]


class TestClass:
    a, b = unpack_fixture("a,b", c, in_cls=True)

    def test_function(self, a, b):
        assert a[0] == b
