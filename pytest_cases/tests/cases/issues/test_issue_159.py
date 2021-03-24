from pytest_cases import parametrize_with_cases, fixture


@fixture
def my_fix():  # dummy fixture to ensure we don't get lazy values
    pass


class CaseGroup(object):
    def case_first_lazy(self):
        return 1

    def case_second_fixture(self, my_fix):
        return 1


@parametrize_with_cases("x", cases=(CaseGroup.case_first_lazy, CaseGroup.case_second_fixture))
def test_parametrize_with_single_case_method_unbound(x):
    assert x == 1


@parametrize_with_cases("x", cases=(CaseGroup().case_first_lazy, CaseGroup().case_second_fixture))
def test_parametrize_with_single_case_method_bound(x):
    assert x == 1


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_parametrize_with_single_case_method_unbound[first_lazy]',
        'test_parametrize_with_single_case_method_unbound[second_fixture]',
        'test_parametrize_with_single_case_method_bound[first_lazy]',
        'test_parametrize_with_single_case_method_bound[second_fixture]'
    ]
