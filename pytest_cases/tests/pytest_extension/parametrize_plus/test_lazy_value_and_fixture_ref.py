# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize_plus, lazy_value, fixture_plus, fixture_ref


@fixture_plus
@parametrize_plus("i", [5, 7])
def bfix(i):
    """
    Bfix bfix

    Args:
        i: (int): write your description
    """
    return -i


def val():
    """
    Returns the value of the given function.

    Args:
    """
    return 1


has_pytest_param = hasattr(pytest, 'param')
if not has_pytest_param:
    @parametrize_plus("a", [lazy_value(val),
                            fixture_ref(bfix),
                            lazy_value(val, id='A')])
    def test_foo_single(a):
        """here the fixture is used for both parameters at the same time"""
        assert a in (1, -5, -7)


    def test_synthesis2(module_results_dct):
        """
        Convert a module_results_synt2.

        Args:
            module_results_dct: (todo): write your description
        """
        assert list(module_results_dct) == ['test_foo_single[a_is_val]',
                                            'test_foo_single[a_is_bfix-5]',
                                            'test_foo_single[a_is_bfix-7]',
                                            'test_foo_single[a_is_A]',
                                            ]


else:
    @parametrize_plus("a", [lazy_value(val),
                            fixture_ref(bfix),
                            pytest.param(lazy_value(val), id='B'),
                            pytest.param(lazy_value(val, id='ignored'), id='C'),
                            lazy_value(val, id='A')])
    def test_foo_single(a):
        """here the fixture is used for both parameters at the same time"""
        assert a in (1, -5, -7)


    def test_synthesis2(module_results_dct):
        """
        Convert a test results.

        Args:
            module_results_dct: (todo): write your description
        """
        assert list(module_results_dct) == ['test_foo_single[a_is_val]',
                                            'test_foo_single[a_is_bfix-5]',
                                            'test_foo_single[a_is_bfix-7]',
                                            'test_foo_single[a_is_P2toP4-B]',
                                            'test_foo_single[a_is_P2toP4-C]',
                                            'test_foo_single[a_is_P2toP4-A]',
                                            ]
