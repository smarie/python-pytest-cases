# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases.plugin import SuperClosure
from pytest_cases import param_fixture, fixture_union

# basic parametrized fixtures
a = param_fixture('a', ['x', 'y'])
b = param_fixture('b', [1, 2])

# union fixtures
c = fixture_union('c', [a, b])
d = fixture_union('d', [b, a], idstyle="explicit")


super_closure = None


def test_fixture_union_harder(c, a, d, request):
    # save super closure for later
    global super_closure
    super_closure = request._pyfuncitem.fixturenames
    print(c, a, d)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        "test_fixture_union_harder[/a-x-d/b-1]",
        "test_fixture_union_harder[/a-x-d/b-2]",
        "test_fixture_union_harder[/a-x-d/a]",
        "test_fixture_union_harder[/a-y-d/b-1]",
        "test_fixture_union_harder[/a-y-d/b-2]",
        "test_fixture_union_harder[/a-y-d/a]",
        "test_fixture_union_harder[/b-1-x-d/b]",
        "test_fixture_union_harder[/b-1-x-d/a]",
        "test_fixture_union_harder[/b-1-y-d/b]",
        "test_fixture_union_harder[/b-1-y-d/a]",
        "test_fixture_union_harder[/b-2-x-d/b]",
        "test_fixture_union_harder[/b-2-x-d/a]",
        "test_fixture_union_harder[/b-2-y-d/b]",
        "test_fixture_union_harder[/b-2-y-d/a]"
    ]


def test_super_closure():
    global super_closure

    # make sure that the closure tree looks good
    assert isinstance(super_closure, SuperClosure)
    assert str(super_closure) == """SuperClosure with 4 alternative closures:
 - ['environment', 'c', 'a', 'request', 'd', 'b'] (filters: c=c[0]=a, d=d[0]=b)
 - ['environment', 'c', 'a', 'request', 'd'] (filters: c=c[0]=a, d=d[1]=a)
 - ['environment', 'c', 'b', 'request', 'a', 'd'] (filters: c=c[1]=b, d=d[0]=b)
 - ['environment', 'c', 'b', 'request', 'a', 'd'] (filters: c=c[1]=b, d=d[1]=a)
The 'super closure list' is ['environment', 'c', 'a', 'request', 'd', 'b']

The fixture tree is :
(environment,c) split: c
 -  (a,request,d) split: d
  -   (b)
  -   ()
 -  (b,request,a,d) split: d
  -   ()
  -   ()
"""
