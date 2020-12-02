from distutils.version import LooseVersion

import itertools as itt
import pytest

from pytest_cases import parametrize, fixture, param_fixtures, fixture_union


def mygen(name):
    """An infinite generator of ids"""
    for i in itt.count():
        yield "%s{%i}" % (name, i)


if LooseVersion(pytest.__version__) < LooseVersion('3.0.0'):
    @fixture
    @parametrize("x", [1, 2], ids=mygen("x"))
    def my_fixture(x):
        return x

    a = param_fixtures("a", ['aa', 'ab'], ids=mygen("a"))

    my_union = fixture_union("my_union", [a], ids=mygen("myunion"))


    def test_foo(my_fixture, my_union, a):
        pass


    def test_synthesis(module_results_dct):
        assert list(module_results_dct) == [
            'test_foo[x{0}-myunion{0}-a{0}]',
            'test_foo[x{0}-myunion{0}-a{1}]',
            'test_foo[x{1}-myunion{0}-a{0}]',
            'test_foo[x{1}-myunion{0}-a{1}]'
        ]

else:
    @fixture
    @parametrize("y", [0, 1], ids=("y{%i}" % i for i in itt.count()))
    @parametrize("x", [1, 2], ids=mygen("x"))
    def my_fixture(x, y):
        return x, y


    a = param_fixtures("a", ['aa', 'ab'], ids=mygen("a"))


    my_union = fixture_union("my_union", [a], ids=mygen("myunion"))


    def test_foo(my_fixture, my_union, a):
        pass


    def test_synthesis(module_results_dct):
        assert list(module_results_dct) == [
            'test_foo[x{0}-y{0}-myunion{0}-a{0}]',
            'test_foo[x{0}-y{0}-myunion{0}-a{1}]',
            'test_foo[x{0}-y{1}-myunion{0}-a{0}]',
            'test_foo[x{0}-y{1}-myunion{0}-a{1}]',
            'test_foo[x{1}-y{0}-myunion{0}-a{0}]',
            'test_foo[x{1}-y{0}-myunion{0}-a{1}]',
            'test_foo[x{1}-y{1}-myunion{0}-a{0}]',
            'test_foo[x{1}-y{1}-myunion{0}-a{1}]'
        ]
