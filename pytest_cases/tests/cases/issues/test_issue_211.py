import pytest
import sys
from pytest_cases import parametrize, parametrize_with_cases


PY3 = sys.version_info >= (3,)


class MyClassName:
    @parametrize(name=("joe", "alice"))
    def case_widget(self, name):
        return name

    def case_foo(self):
        return "foo"


@parametrize_with_cases('val', cases=MyClassName)
def test_function(val, current_cases, request):
    print(val)
    case_id, case_func = current_cases['val']
    print((case_id, case_func))

    if (case_func is MyClassName.case_widget) if PY3 else (case_func == MyClassName.case_widget):
        # workaround to get the parameter, but a bit dirty
        if request.node.callspec.params['widget'].argvalues[0] == "joe":
            assert request.node.name == 'test_function[widget-name=joe]'
            pytest.skip("joe skipped")

    assert request.node.name != 'test_function[widget-name=joe]'


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_function[widget-name=joe]',
        'test_function[widget-name=alice]',
        'test_function[foo]'
    ]
