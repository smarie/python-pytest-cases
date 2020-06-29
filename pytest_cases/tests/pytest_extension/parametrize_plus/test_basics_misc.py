import sys

import pytest

from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_plus
from pytest_cases.fixture_parametrize_plus import _get_argnames_argvalues


def test_argname_error():
    with pytest.raises(ValueError, match="parameter 'a' not found in test function signature"):
        @parametrize_plus("a", [True])
        def test_foo(b):
            pass


PY36 = sys.version_info >= (3, 6)


@pytest.mark.parametrize("tuple_around_single", [False, True])
def test_get_argnames_argvalues(tuple_around_single):

    # legacy way
    # -- 1 argname
    argnames, argvalues = _get_argnames_argvalues('a', (True, 1.25))
    assert argnames == ['a']
    assert argvalues == [True, 1.25]
    # -- several argnames
    argnames, argvalues = _get_argnames_argvalues('a,b', ((True, 1.25), (True, 0)))
    assert argnames == ['a', 'b']
    assert argvalues == [(True, 1.25), (True, 0)]

    # **args only
    # -- 1 argname
    argnames, argvalues = _get_argnames_argvalues(b=[1.25, 0])
    assert argnames == ['b']
    assert argvalues == [1.25, 0]
    # -- several argnames
    argnames, argvalues = _get_argnames_argvalues(a=[True], b=[1.25, 0])
    if PY36:
        assert argnames == ['a', 'b']
    else:
        assert set(argnames) == {'a', 'b'}
    if argnames[-1] == 'b':
        assert argvalues == [(True, 1.25), (True, 0)]
    else:
        assert argvalues == [(1.25, True), (0, True)]

    # --dict version
    # -- 1 argname
    argnames, argvalues = _get_argnames_argvalues(**{'b': [1.25, 0]})
    assert argnames == ['b']
    assert argvalues == [1.25, 0]
    # -- several argnames at once
    argnames, argvalues = _get_argnames_argvalues(**{'a,b': ((True, 1.25), (True, 0))})
    assert argnames == ['a', 'b']
    assert argvalues == [(True, 1.25), (True, 0)]
    # -- several argnames in two entries
    argnames, argvalues = _get_argnames_argvalues(**{'a,b': ((True, 1.25), (True, 0)), 'c': [-1, 2]})
    if not PY36:
        # order is lost
        assert set(argnames) == {'a', 'b', 'c'}
    else:
        assert argnames == ['a', 'b', 'c']

    if argnames[-1] == 'c':
        assert argvalues == [(True, 1.25, -1), (True, 1.25, 2), (True, 0, -1), (True, 0, 2)]
    else:
        # for python < 3.6
        assert argvalues == [(-1, True, 1.25), (-1, True, 0), (2, True, 1.25),  (2, True, 0)]


def format_me(**kwargs):
    if 'a' in kwargs:
        return "a={a},b={b:3d}".format(**kwargs)
    else:
        return "{d}yes".format(**kwargs)


@parametrize_plus("a,b", [(True, -1), (False, 3)], idgen=format_me)
@parametrize_plus("c", [2.1, 0.], idgen="c{c:.1f}")
@parametrize_plus("d", [10], idgen=format_me)
def test_idgen1(a, b, c, d):
    pass


def test_idgen1_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_idgen1, test_id_format='function')
    if sys.version_info > (3, 6):
        assert list(results_dct) == [
            'test_idgen1[10yes-c2.1-a=True,b= -1]',
            'test_idgen1[10yes-c2.1-a=False,b=  3]',
            'test_idgen1[10yes-c0.0-a=True,b= -1]',
            'test_idgen1[10yes-c0.0-a=False,b=  3]'
        ]
    else:
        assert len(results_dct) == 4


@parametrize_plus(idgen="a={a},b={b:.1f} and {c:4d}", **{'a,b': ((True, 1.25), (True, 0.)), 'c': [-1, 2]})
def test_alt_usage1(a, b, c):
    pass


def test_alt_usage1_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_alt_usage1, test_id_format='function')
    if sys.version_info > (3, 6):
        assert list(results_dct) == [
            'test_alt_usage1[a=True,b=1.2 and   -1]',
            'test_alt_usage1[a=True,b=1.2 and    2]',
            'test_alt_usage1[a=True,b=0.0 and   -1]',
            'test_alt_usage1[a=True,b=0.0 and    2]'
        ]
    else:
        assert len(results_dct) == 4


@parametrize_plus(idgen="b{b:.1}", **{'b': (1.25, 0.)})
def test_alt_usage2(b):
    pass


def test_alt_usage2_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_alt_usage2, test_id_format='function')
    assert list(results_dct) == [
        'test_alt_usage2[b1e+00]',
        'test_alt_usage2[b0e+00]'
    ]
