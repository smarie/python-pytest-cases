from pytest_cases import fixture, get_all_cases
from pytest_cases.common_others import AUTO


def mock_parameterization_target():
    """A callable to use as parametrization target."""


@fixture
def get_all_cases_auto_fails():
    """Fail because we ask for AUTO cases in a non-'test_<...>' file."""
    def _fail():
        get_all_cases(mock_parameterization_target, cases=AUTO)
    return _fail
