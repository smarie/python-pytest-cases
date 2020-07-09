import pytest

try: # python 3+
    from math import inf
except ImportError:
    inf = float('inf')

from pytest_cases import case_name
try:  # python 3.5+
    from pytest_cases import CaseData
except ImportError:
    pass


from ..example_code import InfiniteInput


def case_simple():
    # type: () -> CaseData
    """ The simplest case with inputs and outputs """

    ins = dict(a=1, b=2)
    outs = 2, 3

    return ins, outs, None


@case_name("Simplest")
def case_simple_named():
    # type: () -> CaseData
    """ The simplest case but with a custom name using @case_name annotation """

    ins = dict(a=1, b=2)
    outs = 2, 3

    return ins, outs, None


def case_simple_error_type():
    # type: () -> CaseData
    """ An error case with an exception type """

    ins = dict(a=1, b="a_string_not_an_int")
    err = TypeError

    return ins, None, err


def case_simple_error_instance():
    # type: () -> CaseData
    """ An error case with an exception instance """

    ins = dict(a=1, b=inf)
    err = InfiniteInput('b')

    return ins, None, err


def case_simple_error_callable():
    # type: () -> CaseData
    """ An error case with an exception validation callable """

    ins = dict(a=1, b=inf)

    def is_good_error(e):
        return type(e) is InfiniteInput and e.args == ('b',)

    return ins, None, is_good_error


@pytest.mark.skip("skipped on purpose")
def case_skipped():
    """ A skipped case """
    return
