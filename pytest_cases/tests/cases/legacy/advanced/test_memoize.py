# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE, case_tags
from ..utils import nb_pytest_parameters, get_pytest_param

try:  # python 3.2+
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

try:  # python 3.5+
    from pytest_cases import CaseData
except ImportError:
    pass


@lru_cache(maxsize=3)
def load_file(file_name):
    """ This function loads the file and returns contents"""
    print("loading file " + file_name)
    return "<dummy content for " + file_name + ">"


@case_tags('a')
def case_1():
    # type: () -> CaseData
    ins = load_file('file1')
    outs, err = None, None
    return ins, outs, err


@case_tags('a', 'b')
def case_2():
    # type: () -> CaseData
    ins = load_file('file2')
    outs, err = None, None
    return ins, outs, err


@case_tags('b', 'c')
def case_3():
    # type: () -> CaseData
    ins = load_file('file3')
    outs, err = None, None
    return ins, outs, err


@cases_data(module=THIS_MODULE, has_tag='a')
def test_a(case_data  # type: CaseDataGetter
           ):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions


@cases_data(module=THIS_MODULE, has_tag='b')
def test_b(case_data  # type: CaseDataGetter
           ):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions


@cases_data(module=THIS_MODULE)
def test_c(case_data  # type: CaseDataGetter
           ):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # see pytest-cases usage page for suggestions


def test_assert_parametrized():
    """Asserts that all tests are parametrized with the correct number of cases"""

    assert nb_pytest_parameters(test_a) == 1
    param_args = get_pytest_param(test_a, 0)
    assert len(param_args) == 2
    assert param_args[0] == 'case_data'
    assert len(param_args[1]) == 2

    assert nb_pytest_parameters(test_b) == 1
    param_args = get_pytest_param(test_b, 0)
    assert len(param_args) == 2
    assert param_args[0] == 'case_data'
    assert len(param_args[1]) == 2

    assert nb_pytest_parameters(test_c) == 1
    param_args = get_pytest_param(test_c, 0)
    assert len(param_args) == 2
    assert param_args[0] == 'case_data'
    assert len(param_args[1]) == 3
