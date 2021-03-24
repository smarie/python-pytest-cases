import pytest_cases


@pytest_cases.fixture
def two_positive_ints():
    return 1, 2


def case_two_positive_ints(two_positive_ints):
    """ Inputs are two positive integers """
    return two_positive_ints


def case_two_positive_ints2(two_positive_ints):
    """ Inputs are two positive integers """
    return two_positive_ints
