from pytest_cases.plugin import SuperClosure
from pytest_cases import param_fixture, fixture_union

# basic parametrized fixtures
a = param_fixture('a', ['x', 'y'])
b = param_fixture('b', [1, 2])

# union fixtures
c = fixture_union('c', [a, b])
d = fixture_union('d', [b, a])


def test_fixture_union_harder(c, a, d, request):

    # make sure that the closure tree looks good
    super_closure = request._pyfuncitem.fixturenames
    assert isinstance(super_closure, SuperClosure)
    assert str(super_closure) == """SuperClosure with 4 alternative closures:
 - ['c', 'a', 'request', 'd', 'b'] (filters: c=c[0]=a, d=d[0]=b)
 - ['c', 'a', 'request', 'd'] (filters: c=c[0]=a, d=d[1]=a)
 - ['c', 'b', 'request', 'a', 'd'] (filters: c=c[1]=b, d=d[0]=b)
 - ['c', 'b', 'request', 'a', 'd'] (filters: c=c[1]=b, d=d[1]=a)
The 'super closure list' is ['c', 'a', 'request', 'd', 'b']

The fixture tree is :
(c) split: c
 -  (a,request,d) split: d
  -   (b)
  -   ()
 -  (b,request,a,d) split: d
  -   ()
  -   ()
"""

    print(c, a, d)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_fixture_union_harder[c_is_a-x-d_is_b-1]",
                                        "test_fixture_union_harder[c_is_a-x-d_is_b-2]",
                                        "test_fixture_union_harder[c_is_a-x-d_is_a]",
                                        "test_fixture_union_harder[c_is_a-y-d_is_b-1]",
                                        "test_fixture_union_harder[c_is_a-y-d_is_b-2]",
                                        "test_fixture_union_harder[c_is_a-y-d_is_a]",
                                        "test_fixture_union_harder[c_is_b-1-x-d_is_b]",
                                        "test_fixture_union_harder[c_is_b-1-x-d_is_a]",
                                        "test_fixture_union_harder[c_is_b-1-y-d_is_b]",
                                        "test_fixture_union_harder[c_is_b-1-y-d_is_a]",
                                        "test_fixture_union_harder[c_is_b-2-x-d_is_b]",
                                        "test_fixture_union_harder[c_is_b-2-x-d_is_a]",
                                        "test_fixture_union_harder[c_is_b-2-y-d_is_b]",
                                        "test_fixture_union_harder[c_is_b-2-y-d_is_a]"]
