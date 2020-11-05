# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from ..example_code import super_function_i_want_to_test, super_function_i_want_to_test2

from pytest_cases import test_target, case_tags
try:  # python 3.5+
    from pytest_cases import CaseData
except ImportError:
    pass


@test_target(super_function_i_want_to_test)
def case_for_function1():
    """
    Return a function that returns a function arguments.

    Args:
    """
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@test_target(super_function_i_want_to_test2)
def case_for_function2():
    """
    Return a function that returns a function that can be used as a case.

    Args:
    """
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@case_tags(super_function_i_want_to_test, super_function_i_want_to_test2)
def case_for_function_1_and_2():
    """
    Return a function that returns the first two case.

    Args:
    """
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None
