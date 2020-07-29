from pytest_cases import fixture, parametrize, fixture_union, fixture_ref


@fixture(autouse=True)
@parametrize(ie=[-1, 1])
def e(ie):
    return "e%s" % ie


@fixture
def d():
    return "d"


@fixture
def c():
    return "c"


@fixture
@parametrize(ia=[0, 1])
def a(c, d, ia):
    return "a%s" % ia + c + d


@parametrize(i2=['x', 'z'])
def test_2(a, i2):
    assert (a + i2) in ("a0cdx", "a0cdz", "a1cdx", "a1cdz")


@fixture
# @parametrize(ub=(fixture_ref(a), fixture_ref(c)), ib=['x', 'z'])
# >> no: order of kwargs changes across versions
# >> AND besides, using **kwargs style with at least a fixture ref creates a fixture for all parametrization even the ones not using fixture_refs
# see https://github.com/smarie/python-pytest-cases/issues/118
@parametrize(ib=['x', 'z'])
@parametrize(ub=(fixture_ref(a), fixture_ref(c)))
def b(ub, ib):
    return "b%s" % ib + ub


u = fixture_union("u", (a, b))


super_closure = None


def test_1(u, request):
    # store for later
    global super_closure
    super_closure = request._pyfuncitem.fixturenames


def test_closure():
    # make sure that the closure tree looks good
    global super_closure
    assert str(super_closure) == """SuperClosure with 3 alternative closures:
 - ['environment', 'e', 'request', 'u', 'a', 'c', 'd'] (filters: u=u[0]=a)
 - ['environment', 'e', 'request', 'u', 'b', 'b_ub', 'a', 'c', 'd'] (filters: u=u[1]=b, b_ub=b_ub[0]=a)
 - ['environment', 'e', 'request', 'u', 'b', 'b_ub', 'c'] (filters: u=u[1]=b, b_ub=b_ub[1]=c)
The 'super closure list' is ['environment', 'e', 'request', 'u', 'a', 'c', 'd', 'b', 'b_ub']

The fixture tree is :
(environment,e,request,u) split: u
 -  (a,c,d)
 -  (b,b_ub) split: b_ub
  -   (a,c,d)
  -   (c)
"""
