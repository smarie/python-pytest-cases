from pytest_cases import pytest_fixture_plus


@pytest_fixture_plus(unpack_into="foo,bar")
def foobar():
    return "blah", "whatever"


def test_stuff(foo, bar):
    assert foo == "blah" and bar == "whatever"
