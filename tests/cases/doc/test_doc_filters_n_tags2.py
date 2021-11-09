# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from math import sqrt
import pytest

from pytest_cases.common_pytest_marks import has_pytest_param
from pytest_cases import parametrize_with_cases, get_case_id


def case_int_success():
    return 1


def case_negative_int_failure():
    # note that we decide to return the expected type of failure to check it
    return -1, ValueError, "math domain error"


@parametrize_with_cases("data", cases='.', glob="*success")
def test_good_datasets(data):
    assert sqrt(data) > 0


@parametrize_with_cases("data, err_type, err_msg", cases='.', glob="*failure")
def test_bad_datasets(data, err_type, err_msg):
    with pytest.raises(err_type, match=err_msg):
        sqrt(data)


def test_synthesis(module_results_dct):
    if has_pytest_param:
        assert list(module_results_dct) == [
            'test_good_datasets[int_success]',
            'test_bad_datasets[negative_int_failure]'
        ]
    else:
        assert list(module_results_dct) == [
            'test_good_datasets[int_success]',
            'test_bad_datasets[negative_int_failure[0]-negative_int_failure[1]-negative_int_failure[2]]'
        ]


def create_filter(sub_str):
    def my_filter(case_func):
        return sub_str in get_case_id(case_func)
    return my_filter


@parametrize_with_cases("data", cases='.', filter=lambda case_func: "success" in get_case_id(case_func))
def test_good_datasets2(data):
    assert sqrt(data) > 0


@parametrize_with_cases("data, err_type, err_msg", cases='.', filter=create_filter("failure"))
def test_bad_datasets2(data, err_type, err_msg):
    with pytest.raises(err_type, match=err_msg):
        sqrt(data)


def test_synthesis2(module_results_dct):
    if has_pytest_param:
        assert list(module_results_dct) == [
            'test_good_datasets[int_success]',
            'test_bad_datasets[negative_int_failure]',
            'test_synthesis',
            'test_good_datasets2[int_success]',
            'test_bad_datasets2[negative_int_failure]'
        ]
    else:
        assert list(module_results_dct) == [
            'test_good_datasets[int_success]',
            'test_bad_datasets[negative_int_failure[0]-negative_int_failure[1]-negative_int_failure[2]]',
            'test_synthesis',
            'test_good_datasets2[int_success]',
            'test_bad_datasets2[negative_int_failure[0]-negative_int_failure[1]-negative_int_failure[2]]'
        ]
