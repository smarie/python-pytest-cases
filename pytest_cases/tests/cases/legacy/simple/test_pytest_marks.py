# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases.case_parametrizer_legacy import get_pytest_marks_on_function, make_marked_parameter_value


def test_get_pytest_marks():
    """
    Tests that we are able to correctly retrieve the marks on case_func
    :return:
    """
    skip_mark = pytest.mark.skipif(True, reason="why")

    @skip_mark
    def case_func():
        pass

    # extract the marks from a case function
    marks = get_pytest_marks_on_function(case_func, as_decorators=True)

    # check that the mark is the same than a manually made one
    assert len(marks) == 1
    assert str(marks[0]) == str(skip_mark)

    # transform a parameter into a marked parameter
    dummy_case = (1, 2, 3)
    marked_param = make_marked_parameter_value((dummy_case,), marks=marks)
