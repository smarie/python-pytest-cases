# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import parametrize_with_cases


@pytest.fixture()
def dependent_fixture():
    """
    Return the fixture of a given fixture.

    Args:
    """
    return 0


class Foo:
    def case_requirement_1(self, dependent_fixture):
        """
        Return a case_fixture of the case.

        Args:
            self: (todo): write your description
            dependent_fixture: (str): write your description
        """
        return Foo, dependent_fixture + 1

    def case_requirement_2(self, dependent_fixture):
        """
        Compute the case case case.

        Args:
            self: (todo): write your description
            dependent_fixture: (str): write your description
        """
        return Foo, dependent_fixture - 1


def case_requirement_1(dependent_fixture):
    """
    Return the case - matching requirements.

    Args:
        dependent_fixture: (str): write your description
    """
    return case_requirement_1.__module__, dependent_fixture + 2


def case_requirement_2(dependent_fixture):
    """
    Return the case - matching requirement requirements.

    Args:
        dependent_fixture: (str): write your description
    """
    return case_requirement_1.__module__, dependent_fixture - 2


@parametrize_with_cases("a,b", cases=(Foo, "."), prefix="case", debug=True)
def test_functionality(a, b):
    """
    Test if a and b are equal.

    Args:
        a: (todo): write your description
        b: (todo): write your description
    """
    do_assert(test_functionality, a, b)


@parametrize_with_cases("a,b", cases=(".", Foo), prefix="case", debug=True)
def test_functionality_again(a, b):
    """
    Test if two test function that b.

    Args:
        a: (todo): write your description
        b: (todo): write your description
    """
    do_assert(test_functionality_again, a, b)


class TestNested:
    @parametrize_with_cases("a,b", cases=(Foo, "."), prefix="case", debug=True)
    def test_functionality_again2(self, a, b):
        """
        Test if two sets of the two sets of the same.

        Args:
            self: (todo): write your description
            a: (todo): write your description
            b: (todo): write your description
        """
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
    """
    Test for test_synthesis.

    Args:
        module_results_dct: (todo): write your description
    """
    # assert that all fixtures have been used once in all tests
    for host in (test_functionality, test_functionality_again, TestNested.test_functionality_again2):
        assert markers_dict[host] == (set(), set())

    assert list(module_results_dct) == [
        'test_functionality[a_b_is__requirement_1]',
        'test_functionality[a_b_is__requirement_2]',
        'test_functionality[a_b_is__requirement_1_]',
        'test_functionality[a_b_is__requirement_2_]',
        'test_functionality_again[a_b_is__requirement_1_]',  # <- note: same fixtures than previously
        'test_functionality_again[a_b_is__requirement_2_]',  # idem
        'test_functionality_again[a_b_is__requirement_1]',   # idem
        'test_functionality_again[a_b_is__requirement_2]',   # idem
        'test_functionality_again2[a_b_is__requirement_1]',  # idem
        'test_functionality_again2[a_b_is__requirement_2]',  # idem
        'test_functionality_again2[a_b_is__requirement_1_]',  # idem
        'test_functionality_again2[a_b_is__requirement_2_]'  # idem
    ]
