import pytest_cases
from pytest_cases.tests.cases.issues.issue_225.cases import *


@pytest_cases.parametrize_with_cases("case_y", cases=case_y)
def test_xy(case_y):
    assert case_y == 2
