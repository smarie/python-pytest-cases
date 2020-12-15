# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases.common_pytest_marks import PYTEST53_OR_GREATER
from pytest_cases.common_pytest_lazy_values import LazyValue, LazyTuple

from pytest_cases import lazy_value
from pytest_cases.common_pytest import mini_idval


_called = 0


def test_value_ref():
    """
    Tests that our hack for lazy_value works: for old versions of pytest, we make it a subclass
    of int so that pytest id generator (`_idval`) calls "str" on it. For pytest >= 5.3.0 we do not need this hack
    as overriding __name__ is enough.
    :return:
    """
    global _called

    def foo():
        global _called
        _called += 1
        return 1, 2

    a = lazy_value(foo)

    # test that ids will be correctly generated even on old pytest
    assert mini_idval(a, 'a', 1) == 'foo'
    assert 'LazyValue' in repr(a)

    # test that that calls work and the cache works even across copies
    class FakeRequest:
        class FakeNode:
            pass
        
        def __init__(self):
            self.node = FakeRequest.FakeNode()

    fake_request = FakeRequest()
    assert a.get(fake_request) == (1, 2)
    assert a.get(fake_request) == (1, 2)
    assert _called == 1
    assert LazyValue.copy_from(a).get(fake_request) == (1, 2)
    assert _called == 1
    fake_request2 = FakeRequest()
    assert a.get(fake_request2) == (1, 2)
    assert _called == 2
    assert LazyValue.copy_from(a).get(fake_request2) == (1, 2)
    assert _called == 2
    # reset cache context and counter for next steps
    a.get(fake_request)
    _called = 1

    # now do the same test for lazy values used as a tuple of parameters
    new_lv = lazy_value(foo)
    assert not new_lv.has_cached_value()
    assert a.has_cached_value()

    for src in new_lv, a:
        # set the counter according to the state of the cache
        _called = 0 if not src.has_cached_value() else 1
        at = src.as_lazy_tuple(2)

        # test when the tuple is unpacked into several parameters
        if not at.has_cached_value():
            for i, a in enumerate(at):
                # test that ids will be correctly generated even on old pytest
                assert mini_idval(a, 'a', 1) == 'foo[%s]' % i
                assert ('LazyTupleItem(item=%s' % i) in repr(a)
        else:
            # this does not happen in real usage but in case a plugin messes with this
            assert tuple(at) == (1, 2)

        # test when the tuple is not unpacked -
        # note: this is not supposed to happen when @parametrize decorates a test function,
        # it only happens when @parametrize decorates a fixture - indeed in that case we generate the whole id ourselves
        assert str(at) == 'foo'

        # assert that calls work and the cache works even across copies
        assert at.get(fake_request) == (1, 2)
        assert at.get(fake_request) == (1, 2)
        assert _called == 1
        assert LazyTuple.copy_from(at).get(fake_request) == (1, 2)
        assert _called == 1

        assert at.get(fake_request2) == (1, 2)
        assert LazyTuple.copy_from(at).get(fake_request2) == (1, 2)
        assert _called == 2

        # test that retrieving the tuple does not loose the id
        assert str(at) == 'foo'
        assert at.has_cached_value()


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

    if PYTEST53_OR_GREATER:
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

        if PYTEST53_OR_GREATER:
            assert not isinstance(lv, int)
            lv2 = lv.clone()
            assert lv == lv2
            assert not isinstance(lv2, int)
        else:
            assert isinstance(lv, int)
            lv2 = lv.clone(remove_int_base=True)
            assert lv == lv2
            assert not isinstance(lv2, int)
