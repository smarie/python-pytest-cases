# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import fixture, get_current_cases, parametrize, lazy_value, fixture_ref, parametrize_with_cases


def foo():
    return 1, 2


@fixture
def foo_fix():
    return 3, 4


@parametrize("a", [1, lazy_value(foo)])
@parametrize("a1,a2", [(1, 2), lazy_value(foo)])
@parametrize("b1,b2", [(1, 2), lazy_value(foo), foo_fix, (foo_fix, foo_fix), (3, 4)], idstyle="explicit")
def test_foo(a, a1, a2, b1, b2, current_cases, request):
    assert current_cases == {}
    assert get_current_cases(request) == {}


# ----------- fix for issue 213

@parametrize(name=("bar", ))
def case_foo2(name):
    return name


@parametrize_with_cases("a", cases=case_foo2)
def test_foo2(a, current_cases):
    assert current_cases == {'a': ('foo2', case_foo2, {'name': 'bar'})}


# ----------- fix for issue 213 bis

@fixture
def o():
    return "name"


@fixture
@parametrize("a", (fixture_ref(o), 'r'))
def a_fix(a):
    return a


def test_foo3(a_fix, current_cases):
    assert current_cases == {}
