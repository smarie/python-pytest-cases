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


@pytest.mark.parametrize("name, m, expected", [
    ("plain_py_func", a, False,),
    ("partial_func", b, False,),
    ("nested_func", c(), False,),
    ("nested_partial_func", d(), False,),
    # --- class
    ("method_on_instance", Foo().a, False,),
    ("method_unbound", Foo.a, True,),
    ("method_on_class_dict", Foo.__dict__['a'], True),
    ("static_method_on_instance", Foo().b, False,),
    ("static_method_on_class", Foo.b, False,),
    ("static_method_on_class_dict", Foo.__dict__['b'], True,),
    ("class_method_on_instance", Foo().c, False,),
    ("class_method_on_class", Foo.c, False,),
    ("class_method_on_class_dict", Foo.__dict__['c'], True),
    ("descriptor_method_on_instance", Foo().d, False,),
    ("descriptor_method_on_class", Foo.d, False,),
    # --- nested class
    ("cls_nested_py_func", Foo.Nested().e(), False,),
    ("cls_nested_method_on_instance", Foo.Nested().a, False,),
    ("cls_nested_method_unbound", Foo.Nested.a, True,),
    ("cls_nested_method_on_class_dict", Foo.Nested.__dict__['a'], True),
    ("cls_nested_static_method_on_instance", Foo.Nested().b, False,),
    ("cls_nested_static_method_on_class", Foo.Nested.b, False,),
    ("cls_nested_static_method_on_class_dict", Foo.Nested.__dict__['b'], True,),
    ("cls_nested_class_method_on_instance", Foo.Nested().c, False,),
    ("cls_nested_class_method_on_class", Foo.Nested.c, False,),
    ("cls_nested_class_method_on_class_dict", Foo.Nested.__dict__['c'], True),
    ("cls_nested_descriptor_method_on_instance", Foo.Nested().d, False,),
    ("cls_nested_descriptor_method_on_class", Foo.Nested.d, False,),
], ids=lambda x: str(x) if isinstance(x, (str, bytes, bool)) else "")
def test_needs_binding(name, m, expected):

    should_bind = needs_binding(m)
    assert should_bind is expected

    should_bind2, m = needs_binding(m, return_bound=True)
    assert should_bind == should_bind2

    # test the method
    assert m(2) == 4
