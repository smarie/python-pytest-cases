# META
# {'passed': 6, 'skipped': 0, 'failed': 0}
# END META

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
    def test_something(self, msg):
        assert msg in [
            "hello !",  # case_hello
            "hello, overridden you joe !",  # case_basic3 + local class fixture 'name' + fixture 'name'
            "hello, overridden earthling joe !"  # case_basic3 + local class  fixture 'name' + fixture 'name'
        ]


class TestOverrideWithoutParent:
    # Overrides module-level name, doesn't request name at all
    @fixture
    @parametrize("_name", ["hi", "martian"])
    def name(self, _name):
        return _name

    @parametrize_with_cases("msg", cases=".")
    def test_something(self, msg):
        assert msg in [
            "hello !",  # case_hello
            "hello, hi !",  #  case_basic3 + local class fixture 'name'
            "hello, martian !"  #  case_basic3 + local class  fixture 'name'
        ]
