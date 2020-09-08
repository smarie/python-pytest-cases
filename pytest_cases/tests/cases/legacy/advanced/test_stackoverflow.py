# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from ..example_code import super_function_i_want_to_test
from pytest_cases import cases_data, CaseDataGetter
try:
    from pytest_cases import CaseData
except ImportError:
    pass


def case_simple():
    # type: (...) -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


def case_simple2():
    # type: (...) -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


@cases_data(cases=case_simple)
def test_with_cases_decorated(case_data  # type: CaseDataGetter
                              ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o


@cases_data(cases=[case_simple, case_simple2])
def test_with_cases_decorated2(case_data  # type: CaseDataGetter
                               ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o


# from https://stackoverflow.com/a/51199035/7262247
try:  # python 3.2+
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache


@lru_cache(maxsize=3)
def load_file(file_name):
    """ This function loads the file and returns contents"""
    print("loading file " + file_name)
    return "<dummy content for " + file_name + ">"


def case_1():
    # type: (...) -> CaseData
    ins = load_file('file1')
    outs, err = None, None
    return ins, outs, err


def case_2():
    # type: (...) -> CaseData
    ins = load_file('file2')
    outs, err = None, None
    return ins, outs, err


def case_3():
    # type: (...) -> CaseData
    ins = load_file('file3')
    outs, err = None, None
    return ins, outs, err


@cases_data(cases=[case_1, case_2])
def test_a(case_data  # type: CaseDataGetter
           ):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions


@cases_data(cases=[case_2, case_3])
def test_b(case_data    # type: CaseDataGetter
           ):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions


@cases_data(cases=[case_1, case_2, case_3])
def test_c(case_data    # type: CaseDataGetter
           ):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions
