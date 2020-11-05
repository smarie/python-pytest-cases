# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from ..example_code import super_function_i_want_to_test

from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE, case_tags
try:  # python 3.5+
    from pytest_cases import CaseData
except ImportError:
    pass


@case_tags('a', 'b')
def case_a_and_b():
    """
    Return a new case and a 2 - tuple of the case

    Args:
    """
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@case_tags('a')
def case_a():
    """
    Returns a new case that is equal integers.

    Args:
    """
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


def my_tag_filter(case_func):
    """
    Decorator that returns only the tags.

    Args:
        case_func: (todo): write your description
    """
    tags = case_func._pytestcase.tags
    return 'a' in tags or 'b' in tags


@cases_data(module=THIS_MODULE, filter=my_tag_filter)
def test_with_cases_a_or_b(case_data  # type: CaseDataGetter
                           ):
    """
    Evaluate test case test case.

    Args:
        case_data: (dict): write your description
    """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o


@cases_data(module=THIS_MODULE, filter=my_tag_filter)
def test_with_cases_a_and_b(case_data  # type: CaseDataGetter
                            ):
    """
    Evaluate test case test case.

    Args:
        case_data: (dict): write your description
    """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
