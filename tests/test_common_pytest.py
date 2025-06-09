#  Authors: Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-pyfields>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-pyfields/blob/master/LICENSE>
import sys

import pytest
from pytest_cases.common_pytest import list_all_fixtures_in, is_fixture, get_fixture_name, get_fixture_scope

@pytest.fixture
def great_fixture_123987():
    return "hey"


@pytest.fixture(scope='session', name="hey_123988")
def great_fixture_123988():
    return "hey2"


THIS_MODULE = sys.modules[__name__]


def test_is_fixture():
    assert is_fixture(great_fixture_123987)
    assert is_fixture(great_fixture_123988)


def test_get_fixture_name():
    assert get_fixture_name(great_fixture_123987) == "great_fixture_123987"
    # Overridden name
    assert get_fixture_name(great_fixture_123988) == "hey_123988"


def test_get_fixture_scope():
    assert get_fixture_scope(great_fixture_123987) == "function"
    # Overridden scope
    assert get_fixture_scope(great_fixture_123988) == "session"


class Foo:
    def foo(self):
        return


@pytest.mark.parametrize("not_a_fixture", (False, 1, test_is_fixture, Foo, Foo.foo))
def test_is_fixture_negative(not_a_fixture):
    assert not is_fixture(not_a_fixture)


def test_list_all_fixtures_in__return_name():
    all_fixtures = list_all_fixtures_in(THIS_MODULE, return_names=True)
    assert "great_fixture_123987" in all_fixtures
    assert "hey_123988" in all_fixtures


def test_list_all_fixtures_in__return_symbols():
    all_fixtures = list_all_fixtures_in(THIS_MODULE, return_names=False)
    assert great_fixture_123987 in all_fixtures
    assert great_fixture_123988 in all_fixtures
