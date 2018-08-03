from pytest_cases import CaseDataGetter, cases_data

from pytest_cases.tests.example_code import super_function_i_want_to_test, super_function_i_want_to_test2

# the file with case functions
from pytest_cases.tests.intermediate import test_shared_cases


@cases_data(module=test_shared_cases, has_tag=super_function_i_want_to_test)
def test_with_filter(case_data  # type: CaseDataGetter
                     ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o


@cases_data(module=test_shared_cases, has_tag=super_function_i_want_to_test2)
def test_with_filter2(case_data  # type: CaseDataGetter
                      ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test2(**i)
    assert outs == expected_o


@cases_data(module=test_shared_cases)
def test_with_no_filter_all_cases(case_data  # type: CaseDataGetter
                                  ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
    outs = super_function_i_want_to_test2(**i)
    assert outs == expected_o
