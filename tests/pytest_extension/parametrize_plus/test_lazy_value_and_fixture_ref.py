# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize, lazy_value, fixture, fixture_ref


@fixture
@parametrize("i", [5, 7])
def bfix(i):
    return -i


def val():
    return 1


has_pytest_param = hasattr(pytest, 'param')
if not has_pytest_param:
    @parametrize("a", [lazy_value(val),
                            fixture_ref(bfix),
                            lazy_value(val, id='A')])
    def test_foo_single(a):
        """here the fixture is used for both parameters at the same time"""
        assert a in (1, -5, -7)


    def test_synthesis2(module_results_dct):
        assert list(module_results_dct) == ['test_foo_single[val]',
                                            'test_foo_single[bfix-5]',
                                            'test_foo_single[bfix-7]',
                                            'test_foo_single[A]',
                                            ]


else:
    @parametrize("a", [lazy_value(val),
                            fixture_ref(bfix),
                            pytest.param(lazy_value(val), id='B'),
                            pytest.param(lazy_value(val, id='ignored'), id='C'),
                            lazy_value(val, id='A')])
    def test_foo_single(a):
        """here the fixture is used for both parameters at the same time"""
        assert a in (1, -5, -7)


    def test_synthesis2(module_results_dct):
        assert list(module_results_dct) == ['test_foo_single[val]',
                                            'test_foo_single[bfix-5]',
                                            'test_foo_single[bfix-7]',
                                            'test_foo_single[B]',
                                            'test_foo_single[C]',
                                            'test_foo_single[A]',
                                            ]
