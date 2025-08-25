from inspect import iscoroutinefunction
from pytest_cases import fixture, parametrize
from pytest_cases.common_pytest_marks import PYTEST84_OR_GREATER


def test_iscoroutinefunction_fixture():
    @fixture
    async def dummy():
        return

    if PYTEST84_OR_GREATER:
        # See https://github.com/pytest-dev/pytest/pull/12473
        import inspect
        obj = inspect.unwrap(dummy)
    else:
        obj = dummy.__pytest_wrapped__.obj

    assert iscoroutinefunction(obj)


# this covers parametrize aswell as parametrize_with_cases
def test_iscoroutinefunction_parametrize():
    @parametrize("a", [0, 1])
    async def dummy(a):
        return

    assert iscoroutinefunction(dummy)
