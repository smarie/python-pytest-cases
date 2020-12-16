import pytest_cases


def case_x():
    return 42


@pytest_cases.parametrize_with_cases("x", case_x)
def case_y(x):
    return 3*x + 2


@pytest_cases.parametrize_with_cases("y", case_y)
def test_foo(y):
    print(y)
