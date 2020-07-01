import sys
from distutils.version import LooseVersion

import pytest

from pytest_cases import parametrize_plus, lazy_value
from pytest_harvest import get_session_synthesis_dct

from pytest_cases.common_pytest import has_pytest_param, cart_product_pytest, get_marked_parameter_values, \
    extract_parameterset_info
from pytest_cases.common_pytest_lazy_values import is_lazy
from pytest_cases.fixture_parametrize_plus import _get_argnames_argvalues
from ...utils import skip


def test_cart_product_pytest():

    # simple
    names_lst, values = cart_product_pytest(('a', 'b'), ([True], [1, 2]))
    assert names_lst == ['a', 'b']
    assert values == [(True, 1), (True, 2)]

    # multi
    names_lst, values = cart_product_pytest(('a,b', 'c'), ([(True, 1)], [1, 2]))
    assert names_lst == ['a', 'b', 'c']
    assert values == [(True, 1, 1), (True, 1, 2)]

    # marks
    names_lst, values = cart_product_pytest(('a,b', 'c'), ([(True, 1)], [skip(1), 2]))
    assert names_lst == ['a', 'b', 'c']
    assert get_marked_parameter_values(values[0]) == (True, 1, 1)
    assert values[1] == (True, 1, 2)

    # lazy values
    def get_tuple():
        return 3, 4
    names_lst, values = cart_product_pytest(('a', 'b,c'), ([True], [lazy_value(get_tuple, marks=skip), (1, 2)]))
    assert names_lst == ['a', 'b', 'c']
    assert values[0][0] is True
    assert is_lazy(values[0][1])
    assert is_lazy(values[0][2])
    assert values[0][1].get_id() == 'get_tuple[0]'
    assert values[0][2].get_id() == 'get_tuple[1]'
    assert values[1] == (True, 1, 2)


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

    # a mark on any of them
    argnames, argvalues = _get_argnames_argvalues(**{'a,b': (skip(True, 1.25), (True, 0)), 'c': [-1, 2]})
    if has_pytest_param:
        assert argvalues[0].id is None
        assert argvalues[0].marks[0].name == 'skip'
        assert argvalues[0].values == (True, 1.25, -1) if argnames[-1] == 'c' else (-1, True, 1.25)

    # hybrid
    # -- several argnames in two entries
    argnames, argvalues = _get_argnames_argvalues('c', (-1, 2), **{'a,b': ((True, 1.25), (True, 0))})
    assert argnames == ['c', 'a', 'b']
    assert argvalues == [(-1, True, 1.25), (-1, True, 0), (2, True, 1.25), (2, True, 0)]
    # -- several argnames in two entries with marks
    argnames, argvalues = _get_argnames_argvalues('c,d', ((True, -1), skip('hey', 2)), **{'a,b': ((True, 1.25), (True, 0))})
    assert argnames == ['c', 'd', 'a', 'b']
    custom_pids, p_marks, p_values = extract_parameterset_info(argnames, argvalues, check_nb=True)
    assert all(p is None for p in custom_pids)
    assert p_values == [(True, -1, True, 1.25), (True, -1, True, 0), ('hey', 2, True, 1.25), ('hey', 2, True, 0)]
    assert p_marks[0:2] == [None, None]
    if has_pytest_param:
        assert len(p_marks[2]) == 1
        assert p_marks[2][0].name == 'skip'
        assert len(p_marks[3]) == 1
        assert p_marks[3][0].name == 'skip'


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
    if sys.version_info >= (3, 6):
        if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
            assert list(results_dct) == [
                'test_idgen1[10yes-c2.1-a=True,b= -1]',
                'test_idgen1[10yes-c2.1-a=False,b=  3]',
                'test_idgen1[10yes-c0.0-a=True,b= -1]',
                'test_idgen1[10yes-c0.0-a=False,b=  3]'
            ]
        else:
            # the order seems not guaranteed or at least quite different in pytest 2
            assert len(results_dct) == 4
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
