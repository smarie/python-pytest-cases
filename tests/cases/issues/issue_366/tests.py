from pytest_cases import get_all_cases
from pytest_cases.common_others import AUTO


def mock_parameterization_target():
    """A callable to use as parametrization target."""


def test_get_all_cases_auto_works_in_tests_py():
    res = get_all_cases(mock_parameterization_target, cases=AUTO)
    assert isinstance(res, list) and len(res) == 1
    assert res[0].__name__ == "case_one_366"
