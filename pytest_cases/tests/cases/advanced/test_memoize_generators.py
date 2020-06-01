from pytest_cases import cases_data, THIS_MODULE, cases_generator, CaseDataGetter, get_all_cases
from pytest_cases.tests.cases.utils import nb_pytest_parameters, get_pytest_param

try:  # python 3+: type hints
    from pytest_cases import CaseData
except ImportError:
    pass


# @lru_cache(maxsize=3)
@cases_generator("case {i}", i=range(3), lru_cache=True)
def case_gen(i):
    # type: (...) -> CaseData
    print("generating case " + str(i))
    ins = i
    outs, err = None, None
    return ins, outs, err


@cases_data(module=THIS_MODULE)
def test_a(case_data  # type: CaseDataGetter
           ):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    print(i)


@cases_data(module=THIS_MODULE)
def test_b(case_data   # type: CaseDataGetter
           ):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    print(i)


def test_assert_cases_are_here():
    """Asserts that the 3 cases are generated"""
    import sys
    cases = get_all_cases(module=sys.modules[case_gen.__module__])
    assert len(cases) == 3


def test_assert_parametrized():
    """Asserts that test_b is parametrized with the correct number of cases"""

    assert nb_pytest_parameters(test_a) == 1
    param_args = get_pytest_param(test_a, 0)
    assert len(param_args) == 2
    assert param_args[0] == 'case_data'
    assert len(param_args[1]) == 3

    assert nb_pytest_parameters(test_b) == 1
    param_args = get_pytest_param(test_b, 0)
    assert len(param_args) == 2
    assert param_args[0] == 'case_data'
    assert len(param_args[1]) == 3
