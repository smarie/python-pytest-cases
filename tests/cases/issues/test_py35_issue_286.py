import pytest
from inspect import iscoroutinefunction
from pytest_cases import fixture, parametrize

def test_iscoroutinefunction_fixture():
    @fixture
    async def dummy():
        return

    assert iscoroutinefunction(dummy.__pytest_wrapped__.obj)


# this covers parametrize aswell as parametrize_with_cases
def test_iscoroutinefunction_parametrize():
    @parametrize("a", [0, 1])
    async def dummy(a):
        return

    assert iscoroutinefunction(dummy)
