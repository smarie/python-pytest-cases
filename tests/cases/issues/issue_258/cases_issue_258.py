from pytest_cases import case


@case
def case_1():
    return "hello world"


@case
def case_2():
    return "hello mars"
