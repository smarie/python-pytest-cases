from functools import lru_cache
from pytest_cases import CaseData, cases_data, CaseDataGetter, THIS_MODULE, case_tags


@lru_cache(maxsize=3)
def load_file(file_name):
    """ This function loads the file and returns contents"""
    print("loading file " + file_name)
    return "<dummy content for " + file_name + ">"


@case_tags('a')
def case_1() -> CaseData:
    ins = load_file('file1')
    outs, err = None, None
    return ins, outs, err


@case_tags('a', 'b')
def case_2() -> CaseData:
    ins = load_file('file2')
    outs, err = None, None
    return ins, outs, err


@case_tags('b', 'c')
def case_3() -> CaseData:
    ins = load_file('file3')
    outs, err = None, None
    return ins, outs, err


@cases_data(module=THIS_MODULE, has_tag='a')
def test_a(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions


@cases_data(module=THIS_MODULE, has_tag='b')
def test_b(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions


@cases_data(module=THIS_MODULE)
def test_c(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions
