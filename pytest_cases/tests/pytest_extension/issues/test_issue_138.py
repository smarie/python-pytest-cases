import pytest
from pytest_cases import fixture, parametrize, fixture_ref


@fixture
def b():
    print("b")
    return "b"


@parametrize("fixture", [fixture_ref(b),
                         pytest.param(fixture_ref(b))
                         ])
def test(fixture):
    assert fixture == "b"
    print("Test ran fixure %s" % fixture)


@parametrize("fixture,a", [(fixture_ref(b), 1),
                           pytest.param(fixture_ref(b), 1)
                           ])
def test2(fixture, a):
    assert fixture == "b"
    assert a == 1
    print("Test ran fixure %s" % fixture)
