# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from distutils.version import LooseVersion

import pytest

from pytest_cases import lazy_value
from pytest_cases.common_pytest import mini_idval


def test_value_ref():
    """
    Tests that our hack for lazy_value works: for old versions of pytest, we make it a subclass
    of int so that pytest id generator (`_idval`) calls "str" on it. For pytest >= 5.3.0 we do not need this hack
    as overriding __name__ is enough.
    :return:
    """
    def foo():
        return 1, 2

    a = lazy_value(foo)

    # test that ids will be correctly generated even on old pytest
    assert mini_idval(a, 'a', 1) == 'foo'
    assert 'LazyValue' in repr(a)

    # now do the same test for lazy values used as a tuple of parameters
    at = lazy_value(foo).as_lazy_tuple(2)

    # test when the tuple is unpacked into several parameters
    for i, a in enumerate(at):
        # test that ids will be correctly generated even on old pytest
        assert mini_idval(a, 'a', 1) == 'foo[%s]' % i
        assert ('LazyTupleItem(item=%s' % i) in repr(a)

    # test when the tuple is not unpacked -
    # note: this is not supposed to happen when @parametrize decorates a test function,
    # it only happens when @parametrize decorates a fixture - indeed in that case we generate the whole id ourselves
    assert str(at) == 'foo'
    assert not at.retrieved
    # test that retrieving the tuple does not loose the id
    v = at.get()
    assert v == (1, 2)
    assert str(at) == 'foo'
    assert at.retrieved


pytest53 = LooseVersion(pytest.__version__) >= LooseVersion("5.3.0")


def test_lv_clone():
    """ Test that the internal API allows other plugins such as pytest-harvest to easily clone a lazy value without
    inheriting from the hack int base"""
    def foo():
        return 1

    lv = lazy_value(foo, id="hi", marks=pytest.mark.skip)

    assert str(lv) == "hi"
    assert repr(lv).startswith("LazyValue(valuegetter=<function")
    assert ">, _id='hi'," in repr(lv)
    assert "'skip'" in repr(lv)

    if pytest53:
        assert not isinstance(lv, int)
        lv2 = lv.clone()
        assert lv == lv2
        assert not isinstance(lv2, int)
    else:
        assert isinstance(lv, int)
        lv2 = lv.clone(remove_int_base=True)
        assert lv == lv2
        assert not isinstance(lv2, int)


def test_lv_tuple_clone():
    """ Test that the internal API allows other plugins such as pytest-harvest to easily clone a lazy value without
    inheriting from the hack int base (this test is for tuple """
    def foo():
        return 1, 2

    lvt = lazy_value(foo, id="hi", marks=pytest.mark.skip).as_lazy_tuple(2)

    for i, lv in enumerate(lvt):
        assert str(lv) == "hi[%s]" % i
        assert repr(lv).startswith("LazyTupleItem(item=%s, tuple=LazyValue(valuegetter=<function" % i)

        if pytest53:
            assert not isinstance(lv, int)
            lv2 = lv.clone()
            assert lv == lv2
            assert not isinstance(lv2, int)
        else:
            assert isinstance(lv, int)
            lv2 = lv.clone(remove_int_base=True)
            assert lv == lv2
            assert not isinstance(lv2, int)
