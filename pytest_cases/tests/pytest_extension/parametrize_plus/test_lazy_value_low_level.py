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
        pass

    a = lazy_value(foo)

    assert mini_idval(a, 'a', 1) == 'foo'
    assert 'lazy_value' in repr(a)
