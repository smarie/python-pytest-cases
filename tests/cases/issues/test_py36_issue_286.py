import pytest
from inspect import isasyncgenfunction
from pytest_cases import fixture, parametrize

def test_isasyncgenfunction_fixture():
    @fixture
    async def dummy():
        yield

    assert isasyncgenfunction(dummy.__pytest_wrapped__.obj)


# this covers parametrize aswell as parametrize_with_cases
def test_isasyncgenfunction_parametrize():
    @parametrize("a", [0, 1])
    async def dummy(a):
        yield

    assert isasyncgenfunction(dummy)
