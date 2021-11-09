import pytest

from pytest_cases.common_pytest_marks import get_pytest_marks_on_item
from pytest_cases import case, parametrize_with_cases, fixture


@fixture
def my_fix():
    return 2


class CasesFeature:
    @case(tags=["categorical"], marks=pytest.mark.fast)
    def case_no_fixture(self):
        return 1

    @case(tags=["med", "categorical"], marks=pytest.mark.slow)
    def case_fixture(self, my_fix):
        return my_fix


@parametrize_with_cases("data", cases=CasesFeature, has_tag="categorical")
def test_marks(data, request):
    """Make sure that the marks are correctly set"""

    current_marks = get_pytest_marks_on_item(request._pyfuncitem)
    assert len(current_marks) == 1
    if data == 1:
        assert current_marks[0].name == "fast"
    elif data == 2:
        assert current_marks[0].name == "slow"
    else:
        raise AssertionError()
