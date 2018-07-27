from pytest_cases.tests.example_code import super_function_i_want_to_test

from pytest_cases import CaseData, cases_data, CaseDataGetter, THIS_MODULE


def case_simple() -> CaseData:
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


def case_simple2() -> CaseData:
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@cases_data(module=THIS_MODULE)
def test_with_cases_decorated(case_data: CaseDataGetter):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
