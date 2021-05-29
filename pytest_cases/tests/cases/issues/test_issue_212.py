import sys
from pytest_cases import parametrize, parametrize_with_cases


PY3 = sys.version_info >= (3,)


class MyClassName:
    def case_foo(self):
        return "fooval"


@parametrize_with_cases('val', cases=MyClassName)
def test_function_basic_parametrize(val, current_cases):
    assert val == "fooval"

    case_id, case_func, case_paramz = current_cases['val']
    assert case_id == "foo"
    if PY3:
        assert case_func is MyClassName.case_foo
    else:
        assert case_func == MyClassName.case_foo
    assert case_paramz == {}


class MyClassNameTuple:
    def case_foo(self):
        return 1, 2


@parametrize_with_cases('a,b', cases=MyClassNameTuple)
def test_function_tuple_basic_parametrize(a, b, current_cases):
    assert (a, b) == (1, 2)

    case_id, case_func, case_paramz = current_cases['a']
    assert current_cases['a'] == current_cases['b']
    assert case_id == "foo"
    if PY3:
        assert case_func is MyClassNameTuple.case_foo
    else:
        assert case_func == MyClassNameTuple.case_foo

    assert case_paramz == {}


class MyClassName2:
    def case_bar(self):
        return "barval"

    @parametrize(dummy=['a'])
    def case_foo(self, dummy):
        return "fooval"


@parametrize_with_cases('val', cases=MyClassName2)
def test_function_nested_parametrize(val, current_cases):
    ref = {
        "barval": (MyClassName2.case_bar, {}),
        "fooval": (MyClassName2.case_foo, {"dummy": "a"})
    }

    case_id, case_func, case_paramz = current_cases['val']
    assert case_id == val[:3]

    if PY3:
        assert case_func is ref[val][0]
    else:
        assert case_func == ref[val][0]

    assert case_paramz == ref[val][1]
