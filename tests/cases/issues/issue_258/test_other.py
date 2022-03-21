from pytest_cases import case


@case
def case_1():
    return "hello test_other"


@case
def case_2():
    return "hi test_other"
