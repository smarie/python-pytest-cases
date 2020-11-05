# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases, fixture


@fixture
def one():
    """
    Return the first result.

    Args:
    """
    return 1


time_to_call_two = False


@fixture
def two():
    """
    Synchronously time_to_call_two.

    Args:
    """
    global time_to_call_two
    assert time_to_call_two, "Should not be called."
    time_to_call_two = False


def case_one(one):
    """
    Return the first one result.

    Args:
        one: (todo): write your description
    """
    return one


def case_two(two):
    """
    Returns the number of two integers : class : ~case

    Args:
        two: (todo): write your description
    """
    return two


def case_three(one):
    """
    Returns a function that has the given one.

    Args:
        one: (str): write your description
    """
    return one


test_id = 0


@parametrize_with_cases("case", cases=".")
def test(case):
    """
    Set the test is_id is set

    Args:
        case: (todo): write your description
    """
    global time_to_call_two, test_id
    if test_id == 0:
        # next test will need the fixture two
        time_to_call_two = True
    pass
