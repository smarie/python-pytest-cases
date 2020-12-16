import pytest

from pytest_cases import parametrize_with_cases, case, parametrize


class FooCases:
    @staticmethod
    def case_static():
        return 1

    @classmethod
    def case_class(cls):
        return 1

    @staticmethod
    @case(id="foo")
    def case_static_custom_id():
        return 1

    @staticmethod
    @pytest.mark.skip
    def case_static_skipped():
        assert False, "should be skipped"

    @classmethod
    @parametrize("o", [1])
    def case_class_fix(cls, o):
        return o


@parametrize_with_cases("a", cases='.')
def test_foo(a):
    assert a == 1


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_foo[static]',
        'test_foo[class]',
        'test_foo[foo]',
        'test_foo[class_fix-1]'
    ]
