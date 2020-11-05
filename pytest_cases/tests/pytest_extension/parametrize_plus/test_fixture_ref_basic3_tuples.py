# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import pytest_parametrize_plus, fixture_ref, pytest_fixture_plus


@pytest_fixture_plus
@pytest.mark.parametrize('val', ['b', 'c'])
def myfix(val):
    """
    Fixmeience function

    Args:
        val: (float): write your description
    """
    return val


@pytest_fixture_plus
@pytest.mark.parametrize('val', [0, -1])
def myfix2(val):
    """
    Convert a python value

    Args:
        val: (float): write your description
    """
    return val


@pytest_fixture_plus
@pytest.mark.parametrize('val', [('d', 3),
                                 ('e', 4)])
def my_tuple(val):
    """
    Convert a tuple of integers.

    Args:
        val: (float): write your description
    """
    return val


@pytest_parametrize_plus('p,q', [('a', 1),
                                 (fixture_ref(myfix), 2),
                                 (fixture_ref(myfix), fixture_ref(myfix2)),
                                 (fixture_ref(myfix), fixture_ref(myfix)),
                                 fixture_ref(my_tuple)])
def test_prints(p, q):
    """
    Test if x [ q

    Args:
        p: (todo): write your description
        q: (todo): write your description
    """
    print(p, q)


def test_synthesis(module_results_dct):
    """
    Test for test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_prints[p_q_is_a-1]',
                                        'test_prints[p_q_is_P1-b]',
                                        'test_prints[p_q_is_P1-c]',
                                        'test_prints[p_q_is_P2-b-0]',
                                        'test_prints[p_q_is_P2-b--1]',
                                        'test_prints[p_q_is_P2-c-0]',
                                        'test_prints[p_q_is_P2-c--1]',
                                        'test_prints[p_q_is_P3-b]',
                                        'test_prints[p_q_is_P3-c]',
                                        "test_prints[p_q_is_my_tuple-val0]",
                                        "test_prints[p_q_is_my_tuple-val1]"
                                        ]
