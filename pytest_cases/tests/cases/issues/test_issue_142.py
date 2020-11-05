import pytest

from pytest_cases import parametrize_with_cases


@pytest.mark.parametrize('dummy_amount', [1, 0, -1])
def case_amount(dummy_amount):
    """
    : param dummy amount of a given dummy amount.

    Args:
        dummy_amount: (todo): write your description
    """
    return dummy_amount


@parametrize_with_cases('dummy_amount', cases=".", prefix="case_amount")
def test_empty_prefix(dummy_amount):
    """
    Test if the given dummy prefix is empty.

    Args:
        dummy_amount: (todo): write your description
    """
    pass


def test_synthesis(module_results_dct):
    """
    Test for test_results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == [
        'test_empty_prefix[<empty_case_id>-1]',
        'test_empty_prefix[<empty_case_id>-0]',
        'test_empty_prefix[<empty_case_id>--1]'
    ]
