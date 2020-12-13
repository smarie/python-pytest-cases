import pytest_cases


@pytest_cases.parametrize(x=[])
def case_empty(x):
    return x  # pragma: no cover


@pytest_cases.parametrize_with_cases("x", case_empty)
def test_empty_parameter_set(x):
    assert False  # pragma: no cover
