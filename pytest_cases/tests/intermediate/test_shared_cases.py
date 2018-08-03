from pytest_cases.tests.example_code import super_function_i_want_to_test, super_function_i_want_to_test2

from pytest_cases import test_target, case_tags
try:  # python 3.5+
    from pytest_cases import CaseData
except ImportError:
    pass


@test_target(super_function_i_want_to_test)
def case_for_function1():
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@test_target(super_function_i_want_to_test2)
def case_for_function2():
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@case_tags(super_function_i_want_to_test, super_function_i_want_to_test2)
def case_for_function_1_and_2():
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None
