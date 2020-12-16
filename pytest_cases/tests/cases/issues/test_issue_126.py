# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases.common_pytest_marks import PYTEST3_OR_GREATER
from pytest_cases import parametrize_with_cases


@pytest.fixture()
def dependent_fixture():
    return 0


class Foo:
    def case_requirement_1(self, dependent_fixture):
        return Foo, dependent_fixture + 1

    def case_requirement_2(self, dependent_fixture):
        return Foo, dependent_fixture - 1


def case_requirement_1(dependent_fixture):
    return case_requirement_1.__module__, dependent_fixture + 2


def case_requirement_2(dependent_fixture):
    return case_requirement_1.__module__, dependent_fixture - 2


@parametrize_with_cases("a,b", cases=(Foo, "."), prefix="case", debug=True)
def test_functionality(a, b):
    do_assert(test_functionality, a, b)


@parametrize_with_cases("a,b", cases=(".", Foo), prefix="case", debug=True)
def test_functionality_again(a, b):
    do_assert(test_functionality_again, a, b)


class TestNested:
    @parametrize_with_cases("a,b", cases=(Foo, "."), prefix="case", debug=True)
    def test_functionality_again2(self, a, b):
        do_assert(TestNested.test_functionality_again2, a, b)


# init our markers
markers_dict = {}
for host in (test_functionality, test_functionality_again, TestNested.test_functionality_again2):
    markers_dict[host] = ({-1, 1}, {-2, 2})  # [0] is for cases in Foo, [1] is for cases in module


def do_assert(host, a, b):
    """used in tests below to make sure that all cases are used"""
    if a is Foo:
        markers_dict[host][0].remove(b)
    elif a == case_requirement_1.__module__:
        markers_dict[host][1].remove(b)
    else:
        raise ValueError()


def test_synthesis(module_results_dct):
    # assert that all fixtures have been used once in all tests
    for host in (test_functionality, test_functionality_again, TestNested.test_functionality_again2):
        assert markers_dict[host] == (set(), set())

    if PYTEST3_OR_GREATER:
        assert list(module_results_dct) == [
            'test_functionality[_requirement_10]',
            'test_functionality[_requirement_20]',
            'test_functionality[_requirement_11]',
            'test_functionality[_requirement_21]',
            'test_functionality_again[_requirement_10]',  # <- note: same fixtures than previously
            'test_functionality_again[_requirement_20]',  # idem
            'test_functionality_again[_requirement_11]',   # idem
            'test_functionality_again[_requirement_21]',   # idem
            'test_functionality_again2[_requirement_10]',  # idem
            'test_functionality_again2[_requirement_20]',  # idem
            'test_functionality_again2[_requirement_11]',  # idem
            'test_functionality_again2[_requirement_21]'  # idem
        ]
    else:
        # In old pytest the numbering seem a little more rough/simple
        assert list(module_results_dct) == [
            'test_functionality[0_requirement_1]',
            'test_functionality[1_requirement_2]',
            'test_functionality[2_requirement_1]',
            'test_functionality[3_requirement_2]',
            'test_functionality_again[0_requirement_1]',
            'test_functionality_again[1_requirement_2]',
            'test_functionality_again[2_requirement_1]',
            'test_functionality_again[3_requirement_2]',
            'test_functionality_again2[0_requirement_1]',
            'test_functionality_again2[1_requirement_2]',
            'test_functionality_again2[2_requirement_1]',
            'test_functionality_again2[3_requirement_2]'
        ]
