import pytest

from pytest_cases.common_pytest_marks import PYTEST421_OR_GREATER, PYTEST54_OR_GREATER
from pytest_cases import parametrize_with_cases, case


@pytest.mark.parametrize('dummy_amount', [1, 0, -1])
def case_amount(dummy_amount):
    return dummy_amount


@parametrize_with_cases('dummy_amount', cases=".", prefix="case_amount")
def test_empty_prefix(dummy_amount):
    pass


@case(id="")
def case_dummy():
    return 0


@case(id="")
@pytest.mark.parametrize('dummy_amount', [1])
def case_dummy2(dummy_amount):
    return dummy_amount


@parametrize_with_cases('dummy_amount', cases=(case_dummy, case_dummy2))
def test_empty_caseid_both(dummy_amount):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_empty_prefix[<empty_case_id>-1]',
        'test_empty_prefix[<empty_case_id>-0]',
        'test_empty_prefix[<empty_case_id>--1]',
        'test_empty_caseid_both[%s]' % ("0" if PYTEST421_OR_GREATER else "test_empty_caseid_both_dummy_amount0"),
        'test_empty_caseid_both[%s-1]' % ("1" if PYTEST421_OR_GREATER else "test_empty_caseid_both_dummy_amount1"),
    ]
