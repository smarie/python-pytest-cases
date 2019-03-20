import pytest

from pytest_cases.common import transform_marks_into_decorators
from pytest_cases.main import get_pytest_marks_on_function, make_marked_parameter_value


@pytest.mark.skipif(True, reason="why")
def case_func():
    pass


def test_get_pytest_marks():
    """
    Tests that we are able to correctly retrieve the marks on case_func
    :return:
    """
    # extract the marks from a case function
    marks = get_pytest_marks_on_function(case_func)
    # transform them into decorators
    marks = transform_marks_into_decorators(marks)
    # check that the mark is the same than a manually made one
    assert len(marks) == 1
    assert str(marks[0]) == str(pytest.mark.skipif(True, reason="why"))

    # transform a parameter into a marked parameter
    dummy_case = (1, 2, 3)
    marked_param = make_marked_parameter_value(dummy_case, marks=marks)
