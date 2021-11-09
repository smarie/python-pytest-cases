# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import fixture_union, fixture, NOT_USED


@fixture(params=[1, 2, 3])
def lower(request):
    return "i" * request.param


# @fixture(params=[1, 2])
# def upper(request):
#     return "I" * request.param

@pytest.fixture(params=[1, 2])
def upper(request):
    # Just for the remark: this fixture does not use fixture
    # so we have to explicitly discard the 'NOT_USED' cases
    if request.param is not NOT_USED:
        return "I" * request.param


fixture_union('all', ['lower', 'upper'])


def test_all(all):
    print(all)


def test_synthesis(module_results_dct):
    """Use pytest-harvest to check that the list of executed tests is correct """

    assert list(module_results_dct) == [
        'test_all[/lower-1]',
        'test_all[/lower-2]',
        'test_all[/lower-3]',
        'test_all[/upper-1]',
        'test_all[/upper-2]'
    ]
