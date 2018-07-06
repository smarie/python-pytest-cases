from pytest_cases.tests.example_code import super_function_i_want_to_test

from pytest_cases import CaseData, cases_data, CaseDataGetter, THIS_MODULE, case_tags


@case_tags('a', 'b')
def case_a_and_b() -> CaseData:
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@case_tags('a')
def case_a() -> CaseData:
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


from mini_lambda import InputVar, _
tags = InputVar('tags', list)


@cases_data(module=THIS_MODULE, filter=_(tags.contains('a') | tags.contains('b')))
def test_with_cases_a_or_b(case_data: CaseDataGetter):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o


@cases_data(module=THIS_MODULE, filter=_(tags.contains('a') & tags.contains('b')))
def test_with_cases_a_and_b(case_data: CaseDataGetter):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
