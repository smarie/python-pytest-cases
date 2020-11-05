# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize_plus, lazy_value, fixture_plus, fixture_ref


@fixture_plus
@parametrize_plus("i", [13, 11])
def tfix(i):
    """
    Return the tfix of the two - dimensional integer

    Args:
        i: (int): write your description
    """
    return i, i+2


@fixture_plus
@parametrize_plus("i", [5, 7])
def vfix(i):
    """
    Fixme :

    Args:
        i: (int): write your description
    """
    return -i


def valtuple():
    """
    Return a tuple of ( x y ) tuples.

    Args:
    """
    return 1, 2


def val():
    """
    Returns the value of the given function.

    Args:
    """
    return 1


flag = False


def valtuple_toskip():
    """
    Convert a tuple of integers representing a tuple of integers.

    Args:
    """
    return 15, 2


def valtuple_only_right_when_lazy():
    """
    Return a tuple with the first two numeric.

    Args:
    """
    global flag
    if flag:
        return 0, -1
    else:
        raise ValueError("not yet ready ! you should call me later ")


has_pytest_param = hasattr(pytest, 'param')
if not has_pytest_param:
    @parametrize_plus("a,b", [lazy_value(valtuple),
                              lazy_value(valtuple, id='A'),
                              fixture_ref(tfix),
                              (fixture_ref(vfix), lazy_value(val)),
                              (lazy_value(val, id='B'), fixture_ref(vfix)),
                              (fixture_ref(vfix), fixture_ref(vfix)),
                              ], debug=True)
    def test_foo_multi(a, b):
        """here the fixture is used for both parameters at the same time"""
        global flag
        flag = True
        assert (a, b) in ((1, 2), (1, 1), (13, 15), (11, 13), (-5, 1), (-7, 1), (1, -5), (1, -7), (-5, -5), (-7, -7))


    def test_synthesis2(module_results_dct):
        """
        Convert a test results.

        Args:
            module_results_dct: (todo): write your description
        """
        assert list(module_results_dct) == ['test_foo_multi[a_b_is_P0toP1-valtuple]',
                                            'test_foo_multi[a_b_is_P0toP1-A]',
                                            'test_foo_multi[a_b_is_tfix-13]',
                                            'test_foo_multi[a_b_is_tfix-11]',
                                            'test_foo_multi[a_b_is_P3-5]',
                                            'test_foo_multi[a_b_is_P3-7]',
                                            'test_foo_multi[a_b_is_P4-5]',
                                            'test_foo_multi[a_b_is_P4-7]',
                                            'test_foo_multi[a_b_is_P5-5]',
                                            'test_foo_multi[a_b_is_P5-7]'
                                            ]

else:
    @parametrize_plus("a,b", [lazy_value(valtuple),
                              pytest.param(lazy_value(valtuple, id='A')),
                              pytest.param(lazy_value(valtuple_toskip), id='Wrong', marks=pytest.mark.skip),
                              fixture_ref(tfix),
                              (fixture_ref(vfix), lazy_value(val)),
                              pytest.param(lazy_value(val), fixture_ref(vfix), id='B'),
                              (fixture_ref(vfix), fixture_ref(vfix)),
                              ], debug=True)
    def test_foo_multi(a, b):
        """here the fixture is used for both parameters at the same time"""
        global flag
        flag = True
        assert (a, b) in ((1, 2), (1, 1), (13, 15), (11, 13), (-5, 1), (-7, 1), (1, -5), (1, -7), (-5, -5), (-7, -7))


    def test_synthesis2(module_results_dct):
        """
        Convert a test results.

        Args:
            module_results_dct: (todo): write your description
        """
        assert list(module_results_dct) == ['test_foo_multi[a_b_is_P0toP2-valtuple]',
                                            'test_foo_multi[a_b_is_P0toP2-A]',
                                            'test_foo_multi[a_b_is_tfix-13]',
                                            'test_foo_multi[a_b_is_tfix-11]',
                                            'test_foo_multi[a_b_is_P4-5]',
                                            'test_foo_multi[a_b_is_P4-7]',
                                            'test_foo_multi[B-5]',
                                            'test_foo_multi[B-7]',
                                            'test_foo_multi[a_b_is_P6-5]',
                                            'test_foo_multi[a_b_is_P6-7]'
                                            ]
