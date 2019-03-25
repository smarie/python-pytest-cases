import pytest
from pytest_cases import param_fixture, param_fixtures


# create a single parameter fixture
my_parameter = param_fixture("my_parameter", [1, 2, 3, 4])


@pytest.fixture
def fixture_uses_param(my_parameter):
    return my_parameter


def test_uses_param(my_parameter, fixture_uses_param):
    # check that the parameter injected in both is the same
    assert my_parameter == fixture_uses_param


# -----
# create a 2-tuple parameter fixture
arg1, arg2 = param_fixtures("arg1, arg2", [(1, 2), (3, 4)])


@pytest.fixture
def fixture_uses_param2(arg2):
    return arg2


def test_uses_param2(arg1, arg2, fixture_uses_param2):
    # check that the parameter injected in both is the same
    assert arg2 == fixture_uses_param2
    assert arg1, arg2 in [(1, 2), (3, 4)]


def test_synthesis(module_results_dct):
    """Use pytest-harvest to check that the list of executed tests is correct """

    assert list(module_results_dct) == ['test_uses_param[1]',
                                        'test_uses_param[2]',
                                        'test_uses_param[3]',
                                        'test_uses_param[4]',
                                        'test_uses_param2[1-2]',
                                        'test_uses_param2[3-4]']
