# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import CaseDataGetter, cases_data

from ..example_code import super_function_i_want_to_test, super_function_i_want_to_test2

# the file with case functions
from . import test_shared_cases


@cases_data(module=test_shared_cases, has_tag=super_function_i_want_to_test)
def test_with_filter(case_data  # type: CaseDataGetter
                     ):
    """
    Assigns the test data to the test case.

    Args:
        case_data: (dict): write your description
    """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o


@cases_data(module=test_shared_cases, has_tag=super_function_i_want_to_test2)
def test_with_filter2(case_data  # type: CaseDataGetter
                      ):
    """
    Assign test_data to test2.

    Args:
        case_data: (dict): write your description
    """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test2(**i)
    assert outs == expected_o


@cases_data(module=test_shared_cases)
def test_with_no_filter_all_cases(case_data  # type: CaseDataGetter
                                  ):
    """
    Test if all test case - insensitive test_filter

    Args:
        case_data: (dict): write your description
    """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
    outs = super_function_i_want_to_test2(**i)
    assert outs == expected_o
