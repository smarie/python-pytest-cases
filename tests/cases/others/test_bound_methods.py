import sys
from functools import partial

import pytest

from pytest_cases.common_others import needs_binding


def a(foo, bar=None):
    return foo * 2


b = partial(a, bar=1)


def c():
    def _c(foo):
        return foo * 2
    return _c


def d():
    def _d(foo, bar=None):
        return foo * 2
    return partial(_d, bar=1)


class Foo(object):

    def a(self, foo):
        assert isinstance(self, Foo)
        return foo * 2

    @staticmethod
    def b(foo):
        return foo * 2

    @classmethod
    def c(cls, foo):
        assert issubclass(cls, Foo)
        return foo * 2

    class MyDesc(object):
        def __get__(self, instance, owner):
            def descriptor_method(foo):
                return foo * 2
            return descriptor_method

    d = MyDesc()

    def e(self):
        def nested(foo):
            return foo * 2

        return nested

    class Nested(object):
        def a(self, foo):
            assert isinstance(self, Foo.Nested)
            return foo * 2

        @staticmethod
        def b(foo):
            return foo * 2

        @classmethod
        def c(cls, foo):
            assert issubclass(cls, Foo.Nested)
            return foo * 2

        class MyDesc(object):
            def __get__(self, instance, owner=None):
                def descriptor_method(foo):
                    return foo * 2

                return descriptor_method

        d = MyDesc()

        def e(self):
            def nested(foo):
                return foo * 2

            return nested


ALL_PY = True
PY3_ONLY = sys.version_info >= (3,)


@pytest.mark.parametrize("name, m, expected, supported", [
    ("plain_py_func", a, False, ALL_PY),
    ("partial_func", b, False, ALL_PY),
    ("nested_func", c(), False, ALL_PY),
    ("nested_partial_func", d(), False, ALL_PY),
    # --- class
    ("method_on_instance", Foo().a, False, ALL_PY),
    ("method_unbound", Foo.a, True, ALL_PY),
    ("method_on_class_dict", Foo.__dict__['a'], True, PY3_ONLY),
    ("static_method_on_instance", Foo().b, False, ALL_PY),
    ("static_method_on_class", Foo.b, False, ALL_PY),
    ("static_method_on_class_dict", Foo.__dict__['b'], True, ALL_PY),
    ("class_method_on_instance", Foo().c, False, ALL_PY),
    ("class_method_on_class", Foo.c, False, ALL_PY),
    ("class_method_on_class_dict", Foo.__dict__['c'], True, PY3_ONLY),
    ("descriptor_method_on_instance", Foo().d, False, ALL_PY),
    ("descriptor_method_on_class", Foo.d, False, ALL_PY),
    # --- nested class
    ("cls_nested_py_func", Foo.Nested().e(), False, ALL_PY),
    ("cls_nested_method_on_instance", Foo.Nested().a, False, ALL_PY),
    ("cls_nested_method_unbound", Foo.Nested.a, True, ALL_PY),
    ("cls_nested_method_on_class_dict", Foo.Nested.__dict__['a'], True, PY3_ONLY),
    ("cls_nested_static_method_on_instance", Foo.Nested().b, False, ALL_PY),
    ("cls_nested_static_method_on_class", Foo.Nested.b, False, ALL_PY),
    ("cls_nested_static_method_on_class_dict", Foo.Nested.__dict__['b'], True, ALL_PY),
    ("cls_nested_class_method_on_instance", Foo.Nested().c, False, ALL_PY),
    ("cls_nested_class_method_on_class", Foo.Nested.c, False, ALL_PY),
    ("cls_nested_class_method_on_class_dict", Foo.Nested.__dict__['c'], True, PY3_ONLY),
    ("cls_nested_descriptor_method_on_instance", Foo.Nested().d, False, ALL_PY),
    ("cls_nested_descriptor_method_on_class", Foo.Nested.d, False, ALL_PY),
], ids=lambda x: str(x) if isinstance(x, (str, bytes, bool)) else "")
def test_needs_binding(name, m, expected, supported):

    if not supported:
        pytest.skip("Not supported on this version of python")

    should_bind = needs_binding(m)
    assert should_bind is expected

    should_bind2, m = needs_binding(m, return_bound=True)
    assert should_bind == should_bind2

    # test the method
    assert m(2) == 4
