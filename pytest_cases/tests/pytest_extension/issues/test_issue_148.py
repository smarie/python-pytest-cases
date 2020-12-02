import itertools as itt

from pytest_cases import parametrize, fixture


def mygen():
    """An infinite generator of ids"""
    for i in itt.count():
        yield "x{%i}" % i


@fixture()
@parametrize("y", [0, 1], ids=("x{%i}" % i for i in itt.count()))
@parametrize("x", [1, 2], ids=mygen())
def my_fixture(x, y):
    return x, y


def test_foo(my_fixture):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_foo[x{0}-x{0}]',
        'test_foo[x{0}-x{1}]',
        'test_foo[x{1}-x{0}]',
        'test_foo[x{1}-x{1}]'
    ]
