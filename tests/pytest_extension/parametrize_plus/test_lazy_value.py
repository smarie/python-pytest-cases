# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize, lazy_value


def valtuple():
    return 1, 2


def val_skipped_on_old_pytest():
    return "what"


def val():
    return 1


@parametrize("a", [lazy_value(val),
                   pytest.param(lazy_value(val_skipped_on_old_pytest), marks=pytest.mark.skip),
                   pytest.param(lazy_value(val), id='B'),
                   pytest.param(lazy_value(val, id='ignored'), id='C'),
                   lazy_value(val, id='A')])
def test_foo_single(a):
    """here the fixture is used for both parameters at the same time"""
    assert a == 1

flag = False

def valtuple_only_right_when_lazy():
    global flag
    if flag:
        return 0, -1
    else:
        raise ValueError("not yet ready ! you should call me later ")

def valtuple_toskip():
    return 15, 2


@parametrize("a,b", [lazy_value(valtuple),
                     lazy_value(valtuple, id="hello"),
                     lazy_value(valtuple_toskip, marks=pytest.mark.skip),
                     (1, lazy_value(valtuple_toskip, marks=pytest.mark.skip)),
                     pytest.param(lazy_value(valtuple_only_right_when_lazy), id='A'),
                     pytest.param(lazy_value(valtuple_toskip, marks=(pytest.mark.xfail,)), id='Wrong', marks=pytest.mark.skip),
                     (1, lazy_value(val)),
                     pytest.param(1, lazy_value(val), id='B')])
def test_foo_multi(a, b):
    """here the fixture is used for both parameters at the same time"""
    global flag
    flag = True
    assert (a, b) in [(1, 2), (1, 1), (0, -1)]


def test_synthesis2(module_results_dct):
    assert list(module_results_dct) == ['test_foo_single[val]',
                                        'test_foo_single[B]',
                                        'test_foo_single[C]',
                                        'test_foo_single[A]',
                                        'test_foo_multi[valtuple]',
                                        'test_foo_multi[hello]',
                                        'test_foo_multi[A]',
                                        'test_foo_multi[1-val]',
                                        'test_foo_multi[B]']
