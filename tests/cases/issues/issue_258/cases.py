# Imported explicitly or with ".cases"
from pytest_cases import case


@case
def case_1():
    return "hello ."


@case
def case_2():
    return "hi ."
