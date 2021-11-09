# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases, fixture


@fixture
def one():
    return 1


time_to_call_two = False


@fixture
def two():
    global time_to_call_two
    assert time_to_call_two, "Should not be called."
    time_to_call_two = False


def case_one(one):
    return one


def case_two(two):
    return two


def case_three(one):
    return one


test_id = 0


@parametrize_with_cases("case", cases=".")
def test(case):
    global time_to_call_two, test_id
    if test_id == 0:
        # next test will need the fixture two
        time_to_call_two = True
    pass
