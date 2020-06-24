from ..example_code import super_function_i_want_to_test

from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE
try:  # python 3.5+
    from pytest_cases import CaseData
except ImportError:
    pass


def case_simple():
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


def case_simple2():
    # type: () -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@cases_data(module=THIS_MODULE)
def test_with_cases_decorated(case_data  # type: CaseDataGetter
                              ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
