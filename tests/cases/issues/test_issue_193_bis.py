# We make sure that two files requiring the same cases files and importing fixtures can work concurrently
import pytest_cases


from .test_issue_193_cases import case_two_positive_ints, case_two_positive_ints2


@pytest_cases.parametrize_with_cases("x", cases=case_two_positive_ints, debug=True, import_fixtures=True)
def test_bar(x):
    assert x is not None


@pytest_cases.parametrize_with_cases("x", cases=case_two_positive_ints2, debug=True, import_fixtures=True)
def test_bar(x):
    assert x is not None
