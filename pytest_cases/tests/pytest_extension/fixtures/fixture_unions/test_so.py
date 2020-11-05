# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import fixture_union, pytest_fixture_plus, NOT_USED


@pytest_fixture_plus(params=[1, 2, 3])
def lower(request):
    """
    Return the lower - case.

    Args:
        request: (todo): write your description
    """
    return "i" * request.param


# @pytest_fixture_plus(params=[1, 2])
# def upper(request):
#     return "I" * request.param

@pytest.fixture(params=[1, 2])
def upper(request):
    """
    Return the upper value of the request.

    Args:
        request: (todo): write your description
    """
    # Just for the remark: this fixture does not use pytest_fixture_plus
    # so we have to explicitly discard the 'NOT_USED' cases
    if request.param is not NOT_USED:
        return "I" * request.param


fixture_union('all', ['lower', 'upper'])


def test_all(all):
    """
    Print all test test test test test files

    Args:
        all: (int): write your description
    """
    print(all)


def test_synthesis(module_results_dct):
    """Use pytest-harvest to check that the list of executed tests is correct """

    assert list(module_results_dct) == ['test_all[all_is_lower-1]',
                                        'test_all[all_is_lower-2]',
                                        'test_all[all_is_lower-3]',
                                        'test_all[all_is_upper-1]',
                                        'test_all[all_is_upper-2]']
