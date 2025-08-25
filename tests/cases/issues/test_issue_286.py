from inspect import isgeneratorfunction
from pytest_cases import fixture, parametrize
from pytest_cases.common_pytest_marks import PYTEST84_OR_GREATER


def test_isgeneratorfunction_fixture():
    @fixture
    def dummy():
        yield

    if PYTEST84_OR_GREATER:
        # See https://github.com/pytest-dev/pytest/pull/12473
        import inspect
        obj = inspect.unwrap(dummy)
    else:
        obj = dummy.__pytest_wrapped__.obj

    assert isgeneratorfunction(obj)


# this covers parametrize aswell as parametrize_with_cases
def test_isgeneratorfunction_parametrize():
    @parametrize("a", [0, 1])
    def dummy(a):
        yield

    assert isgeneratorfunction(dummy)
