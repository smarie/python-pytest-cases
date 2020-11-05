# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import fixture, parametrize


@fixture(autouse=True)
@parametrize(ie=[-1, 1])
def e(ie):
    """
    Returns a human - like object

    Args:
        ie: (int): write your description
    """
    return "e%s" % ie


@fixture
def d():
    """
    Return the d

    Args:
    """
    return "d"


@fixture
def c():
    """
    Return the c : parameter

    Args:
    """
    return "c"


@fixture
@parametrize(ia=[0, 1])
def a(c, d, ia):
    """
    Return a - > b.

    Args:
        c: (int): write your description
        d: (int): write your description
        ia: (todo): write your description
    """
    return "a%s" % ia + c + d


@parametrize(i2=['x', 'z'])
def test_2(a, i2):
    """
    Èi̇·åıĸæł¥

    Args:
        a: (array): write your description
        i2: (array): write your description
    """
    assert (a + i2) in ("a0cdx", "a0cdz", "a1cdx", "a1cdz")


@fixture
@parametrize(ib=['x', 'z'])
def b(a, c, ib):
    """
    B = b.

    Args:
        a: (int): write your description
        c: (int): write your description
        ib: (int): write your description
    """
    return "b%s" % ib + c + a


def test_1(a, b):
    """
    Compare two matrices

    Args:
        a: (array): write your description
        b: (array): write your description
    """
    assert a in ("a0cd", "a1cd")
    assert a == b[-4:]
    assert b[:-4] in ("bxc", "bzc")
