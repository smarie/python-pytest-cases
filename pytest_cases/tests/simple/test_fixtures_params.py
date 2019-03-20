from pytest_cases import pytest_fixture_plus
import pytest


@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize("arg1", ["one", "two"])
@pytest.mark.parametrize("arg2", ["one", "two"])
def myfix(arg1, arg2):
    return arg1, arg2


def test_one(myfix):
    assert myfix[0] in {"one", "two"}
    assert myfix[1] in {"one", "two"}
    print(myfix)


@pytest_fixture_plus
@pytest.mark.parametrize("arg1, arg2", [
    (1, 2),
    (3, 4),
])
def myfix2(arg1, arg2):
    return arg1, arg2


def test_two(myfix2):
    assert myfix2 in {(1, 2), (3, 4)}
    print(myfix2)


def test_synthesis(module_results_dct):
    """Use pytest-harvest to check that the list of executed tests is correct """
    assert list(module_results_dct) == ['test_one[one-one]',
                                        'test_one[one-two]',
                                        'test_one[two-one]',
                                        'test_one[two-two]',
                                        'test_two[1-2]',
                                        'test_two[3-4]']
