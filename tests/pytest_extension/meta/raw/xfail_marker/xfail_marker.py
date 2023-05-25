# META
# {'passed': 1, 'xfailed': 1, 'failed': 0}
# END META
import pytest
from pytest_cases import parametrize_with_cases

def case_a():
    return "a"

@pytest.mark.xfail
def case_b():
    raise RuntimeError("Expected to Fail")

@parametrize_with_cases("case", cases=".")
def test_cases(case):
    assert case == "a"
