# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import fixture_ref, parametrize, fixture


@fixture
@parametrize("variant", ['A', 'B'])
def book1(variant):
    return variant


@pytest.fixture
def book2():
    return


@parametrize("name", [
    fixture_ref(book1),
    'hi',
    'ih',
    fixture_ref(book2),
])
def test_get_or_create_book(name):
    print(name)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_get_or_create_book[book1-A]',
                                        'test_get_or_create_book[book1-B]',
                                        'test_get_or_create_book[hi]',
                                        'test_get_or_create_book[ih]',
                                        'test_get_or_create_book[book2]']
