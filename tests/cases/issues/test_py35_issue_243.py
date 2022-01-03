import pytest

from pytest_cases import parametrize_with_cases, fixture


def test_missing_self():
    class MyCases:
        def case_forgot_self() -> int:
            return 456

    with pytest.raises(TypeError) as exc_info:
        @parametrize_with_cases(argnames="expected", cases=MyCases)
        def test_foo(expected):
            pass

    assert str(exc_info.value) == ("case method is missing 'self' argument but is not static: %s"
                                   % MyCases.case_forgot_self)


@fixture
def a():
    return


def test_missing_self_params():
    class MyCases:
        def case_fix_forgot_self(a) -> int:
            return a

    with pytest.raises(TypeError) as exc_info:
        @parametrize_with_cases(argnames="expected", cases=MyCases)
        def test_foo(expected):
            pass

    assert str(exc_info.value) == ("case method is missing 'self' argument but is not static: %s"
                                   % MyCases.case_fix_forgot_self)
