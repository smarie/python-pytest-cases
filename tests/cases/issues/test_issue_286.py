import pytest
from inspect import isgeneratorfunction
from pytest_cases import fixture, parametrize

def test_isgeneratorfunction_fixture():
    @fixture
    def dummy():
        yield

    assert isgeneratorfunction(dummy.__pytest_wrapped__.obj)


# this covers parametrize aswell as parametrize_with_cases
def test_isgeneratorfunction_parametrize():
    @parametrize("a", [0, 1])
    def dummy(a):
        yield

    assert isgeneratorfunction(dummy)
