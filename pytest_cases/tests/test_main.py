from math import isfinite

import pytest

from pytest_cases import cases_data, CaseData, unfold_expected_err, extract_cases_from_module
from pytest_cases.tests.example_code import super_function_i_want_to_test


from pytest_cases.tests import test_main_data

# Manual way:
cases = extract_cases_from_module(test_main_data)


@pytest.mark.parametrize('case_data', cases, ids=str)
def test_with_cases_manual(case_data: CaseData):
    """ Example unit test that is automatically parametrized with @cases_data """

    # Grab the test case data (this can trigger parsing, data generation, etc.)
    i, expected_o, expected_e = case_data.get()

    if expected_e is None:
        # Nominal test
        outs = super_function_i_want_to_test(**i)
        assert outs == expected_o

    else:
        # ExpectedError test
        err_type, err_inst, err_checker = unfold_expected_err(expected_e)

        # Exception capture and type check
        with pytest.raises(err_type) as err_info:
            super_function_i_want_to_test(**i)

        # Exception instance check
        if err_inst is not None:
            assert err_info.value == err_inst

        # Additional exception instance check
        if err_checker is not None:
            err_checker(err_info.value)


# Decorator way:
@cases_data(test_main_data)
def test_with_cases_decorated(case_data: CaseData):
    """ Example unit test that is automatically parametrized with @cases_data """

    # Grab the test case data (this can trigger parsing, data generation, etc.)
    i, expected_o, expected_e = case_data.get()

    if expected_e is None:
        # Nominal test
        outs = super_function_i_want_to_test(**i)
        assert outs == expected_o

    else:
        # ExpectedError test
        err_type, err_inst, err_checker = unfold_expected_err(expected_e)

        # Exception capture and type check
        with pytest.raises(err_type) as err_info:
            super_function_i_want_to_test(**i)

        # Exception instance check
        if err_inst is not None:
            assert err_info.value == err_inst

        # Additional exception instance check
        if err_checker is not None:
            err_checker(err_info.value)
