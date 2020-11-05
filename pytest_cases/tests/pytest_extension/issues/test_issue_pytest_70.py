# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import fixture_ref, pytest_parametrize_plus, pytest_fixture_plus


@pytest_fixture_plus
@pytest_parametrize_plus("variant", ['A', 'B'])
def book1(variant):
    """
    Returns a variant of a variant.

    Args:
        variant: (todo): write your description
    """
    return variant


@pytest.fixture
def book2():
    """
    Returns the : meth : class : ~tax.

    Args:
    """
    return


@pytest_parametrize_plus("name", [
    fixture_ref(book1),
    'hi',
    'ih',
    fixture_ref(book2),
])
def test_get_or_create_book(name):
    """
    Todo : pypi.

    Args:
        name: (str): write your description
    """
    print(name)


def test_synthesis(module_results_dct):
    """
    Test if the test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_get_or_create_book[name_is_book1-A]',
                                        'test_get_or_create_book[name_is_book1-B]',
                                        'test_get_or_create_book[name_is_P1toP2-hi]',
                                        'test_get_or_create_book[name_is_P1toP2-ih]',
                                        'test_get_or_create_book[name_is_book2]']
