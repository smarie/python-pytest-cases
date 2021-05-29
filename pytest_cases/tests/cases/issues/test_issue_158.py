import pytest_cases


def case_x():
    return 42


@pytest_cases.parametrize_with_cases("x", case_x)
def case_y(x):
    return 3*x + 2


@pytest_cases.parametrize_with_cases("y", case_y)
def test_foo(y, current_cases):
    print(y)
    # adding this as this example contains an interesting name conflict to challenge current_cases
    assert current_cases == {
        'y': ('y', case_y, {'x': ('x', case_x, {})})
    }
