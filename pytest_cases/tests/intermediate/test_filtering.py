from pytest_cases.tests.example_code import super_function_i_want_to_test

from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE, case_tags
try:  # python 3.5+
    from pytest_cases import CaseData
except ImportError:
    pass


@case_tags('a', 'b')
def case_a_and_b():
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@case_tags('a')
def case_a():
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@cases_data(module=THIS_MODULE, filter=lambda tags: 'a' in tags or 'b' in tags)
def test_with_cases_a_or_b(case_data  # type: CaseDataGetter
                           ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o


@cases_data(module=THIS_MODULE, filter=lambda tags: 'a' in tags and 'b' in tags)
def test_with_cases_a_and_b(case_data  # type: CaseDataGetter
                            ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
