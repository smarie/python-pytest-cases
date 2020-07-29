from collections import defaultdict
from distutils.version import LooseVersion

import pytest

from pytest_cases import fixture, fixture_union


used = defaultdict(lambda: False)
torn_down = defaultdict(lambda: False)


@fixture(scope='session')
def a():
    global used, torn_down
    assert not used['a']
    used['a'] = True
    yield 'a'
    torn_down['a'] = True


@fixture(scope='module')
def b(a):
    global used, torn_down
    assert not used['b']
    used['b'] = True
    yield 'b'
    torn_down['b'] = True


@fixture(scope='function')
def c1(b):
    global used, torn_down
    used['c1'] += 1
    yield 'c1'
    torn_down['c1'] += 1


@fixture(scope='function')
def c2():
    global used, torn_down
    used['c2'] += 1
    yield 'c2'
    torn_down['c2'] += 1


@fixture(scope='function')
def c3(a):
    global used, torn_down
    used['c3'] += 1
    yield 'c3'
    torn_down['c3'] += 1


@fixture(scope='function')
def c4(b):
    global used, torn_down
    used['c4'] += 1
    yield 'c4'
    torn_down['c4'] += 1


d = fixture_union('d', (c1, c2, c3, c4))


def test_foo(d, request):
    super_closure = request._pyfuncitem._fixtureinfo.names_closure

    # in old pytest sorting is different and cannot be done according to scope
    if LooseVersion(pytest.__version__) >= LooseVersion('3.5.0'):
        assert str(super_closure) == """SuperClosure with 4 alternative closures:
 - ['d', 'a', 'b', 'c1', 'request'] (filters: d=d[0]=c1)
 - ['d', 'c2', 'request'] (filters: d=d[1]=c2)
 - ['d', 'a', 'c3', 'request'] (filters: d=d[2]=c3)
 - ['d', 'a', 'b', 'c4', 'request'] (filters: d=d[3]=c4)
The 'super closure list' is ['a', 'b', 'd', 'c1', 'request', 'c2', 'c3', 'c4']

The fixture tree is :
(d) split: d
 -  (c1,request,b,a)
 -  (c2,request)
 -  (c3,request,a)
 -  (c4,request,b,a)
"""


def test_synthesis(module_results_dct):
    assert all(torn_down.values())
    assert list(module_results_dct) == [
        'test_foo[d_is_c1]',
        'test_foo[d_is_c4]',
        'test_foo[d_is_c3]',
        'test_foo[d_is_c2]',
    ]

    for item in ('a', 'b', 'c1', 'c2', 'c3', 'c4'):
        assert used[item] == 1
        assert torn_down[item] == 1
