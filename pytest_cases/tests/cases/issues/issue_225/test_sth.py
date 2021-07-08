import pytest_cases
from .cases import *


@pytest_cases.parametrize_with_cases("case_y", cases=case_y)
def test_xy(case_y):
    assert case_y == 2
