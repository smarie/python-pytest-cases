import six

from pytest_cases import parametrize_with_cases, fixture
from pytest_cases.case_funcs_new import CaseGroupMeta


@fixture
def compute_lazy_values():  # dummy fixture to ensure we don't get lazy values
    pass


@six.add_metaclass(CaseGroupMeta)
class CaseGroup(object):
    def case_first(self, compute_lazy_values):
        return 1

    def case_second(self, compute_lazy_values):
        return 2


@parametrize_with_cases("x", CaseGroup.case_first)
def test_parametrize_with_single_case_method_unbound(x):
    assert x == 1


@parametrize_with_cases("x", CaseGroup().case_first)
def test_parametrize_with_single_case_method_bound(x):
    assert x == 1
