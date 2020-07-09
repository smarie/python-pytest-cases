from pytest_cases import cases_data, CaseDataGetter
from . import test_shared_cases
from ..simple import test_main_cases


# Decorator way:
@cases_data(module=[test_main_cases, test_shared_cases])
def test_with_cases_decorated(case_data  # type: CaseDataGetter
                              ):
    """ Example unit test that is automatically parametrized with @cases_data """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # ...
