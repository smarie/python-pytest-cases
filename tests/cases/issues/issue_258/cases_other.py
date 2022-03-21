# Used by passing the corresponding module `test_other` to `get_all_cases`
# `get_all_cases(test_other)`
from pytest_cases import case


@case
def case_1():
    return "hello cases_other"


@case
def case_2():
    return "hi cases_other"
