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
@parametrize(ub=(fixture_ref(a), fixture_ref(c)), ib=['x', 'z'])
def b(ub, ib):
    return "b%s" % ib + ub


u = fixture_union("u", (a, b))


def test_1(u):
    pass
