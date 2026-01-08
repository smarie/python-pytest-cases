OVERRIDDEN_FIXTURES_TEST_FILE = """
import pytest

@pytest.fixture
def db(): pass

@pytest.fixture
def app(db): pass


# See https://github.com/pytest-dev/pytest/issues/13773
# Issue occurred in collection with Pytest 9+

    
class TestOverrideWithParent:
    # Overrides module-level app, doesn't request `db` directly, only transitively.
    @pytest.fixture
    def app(self, app): pass

    def test_something(self, app): pass



class TestOverrideWithoutParent:
    # Overrides module-level app, doesn't request `db` at all.
    @pytest.fixture
    def app(self): pass

    def test_something(self, app): pass
"""


def test_overridden_fixtures(pytester):
    pytester.makepyfile(OVERRIDDEN_FIXTURES_TEST_FILE)
    result = pytester.runpytest("-p", "pytest_cases.plugin")
    result.assert_outcomes(passed=2)


# Using union fixtures.
OVERRIDDEN_UNION_FIXTURES_TEST_FILE = """
import pytest
from pytest_cases import parametrize, parametrize_with_cases, case, fixture

@fixture
def db(): pass

@fixture
def app(db): pass

def case_hello():
    return "hello !"

@fixture
def surname():
    return "joe"

@fixture
@parametrize("_name", ["you", "earthling"])
def name(_name, surname, app):
    return f"{_name} {surname}"

@case(id="hello_fixture")
def case_basic3(name):
    return "hello, %s !" % name


class TestOverrideWithParent:
    # Overrides module-level name, doesn't request `name` directly, only transitively.
    @fixture
    def name(self, name):
        return "overridden %s" % name

    @parametrize_with_cases("msg", cases=".")
    def test_something(self, msg): pass

class TestOverrideWithoutParent:
    # Overrides module-level name, doesn't request name at all
    @fixture
    @parametrize("_name", ["hi", "martian"])
    def name(self, _name):
        return _name

    @parametrize_with_cases("msg", cases=".")
    def test_something(self, msg): pass
"""


def test_overridden_unions(pytester):
    pytester.makepyfile(OVERRIDDEN_UNION_FIXTURES_TEST_FILE)
    result = pytester.runpytest("-p", "pytest_cases.plugin")
    result.assert_outcomes(passed=6)
