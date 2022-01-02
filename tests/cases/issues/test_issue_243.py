import pytest

from pytest_cases import parametrize_with_cases


def test_missing_self():
    class MyCases:
        def case_one(self) -> int:
            return 123

        def case_two_forgot_self() -> int:
            return 456

    with pytest.raises(TypeError) as exc_info:
        @parametrize_with_cases(argnames="expected", cases=MyCases)
        def test_foo(expected):
            pass

    assert str(exc_info.value) == ("case method is missing 'self' argument but is not static: %s"
                                   % MyCases.case_two_forgot_self)
