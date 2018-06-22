from math import inf
from typing import Tuple

from pytest_cases import case_name, Given, ExpectedNormal, ExpectedError
from pytest_cases.tests.example_code import InfiniteInput


def case_simple() -> Tuple[Given, ExpectedNormal, ExpectedError]:
    """ The simplest case with inputs and outputs """

    ins = dict(a=1, b=2)
    outs = 2, 3

    return ins, outs, None


@case_name("Simple named")
def case_simple_named() -> Tuple[Given, ExpectedNormal, ExpectedError]:
    """ The simplest case but with a custom name using @case_name annotation """

    ins = dict(a=1, b=2)
    outs = 2, 3

    return ins, outs, None


def case_simple_error_type() -> Tuple[Given, ExpectedNormal, ExpectedError]:
    """ An error case with an exception type """

    ins = dict(a=1, b="a_string_not_an_int")
    err = TypeError

    return ins, None, err


def case_simple_error_instance() -> Tuple[Given, ExpectedNormal, ExpectedError]:
    """ An error case with an exception instance """

    ins = dict(a=1, b=inf)
    err = InfiniteInput('b')

    return ins, None, err
