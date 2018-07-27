import pytest

from pytest_cases.tests.example_code import super_function_i_want_to_test

from pytest_cases import CaseData, cases_data, CaseDataGetter, THIS_MODULE, cases_generator


def case_simple(version: str) -> CaseData:
    print("using version " + version)
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


def case_simple2(version: str) -> CaseData:
    print("using version " + version)
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@cases_generator("gen case i={i}, j={j}", i=range(2), j=range(2))
def case_gen(version: str, i, j) -> CaseData:
    print("using version " + version)
    ins = dict(a=i, b=j)
    outs = i+1, j+1
    return ins, outs, None


# the order of the loops will be [for version] > [for case]
@cases_data(module=THIS_MODULE)
@pytest.mark.parametrize("version", ["1.0.0", "2.0.0"])
def test_with_parameters(case_data: CaseDataGetter, version):
    """ This test checks that you can blend with your own pytest fixtures/parameters """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get(version)

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
