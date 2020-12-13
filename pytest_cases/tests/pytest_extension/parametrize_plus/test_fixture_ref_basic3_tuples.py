# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import parametrize, fixture_ref, fixture


@fixture
@pytest.mark.parametrize('val', ['b', 'c'])
def myfix(val):
    return val


@fixture
@pytest.mark.parametrize('val', [0, -1])
def myfix2(val):
    return val


@fixture
@pytest.mark.parametrize('a, b', [('d', 3),
                                 ('e', 4)])
def my_tuple(a, b):
    return a, b


@parametrize('p,q', [('a', 1),
                     (fixture_ref(myfix), 2),
                     (fixture_ref(myfix), fixture_ref(myfix2)),
                     (fixture_ref(myfix), fixture_ref(myfix)),
                     fixture_ref(my_tuple)])
def test_prints(p, q):
    print(p, q)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_prints[a-1]',
        'test_prints[myfix-2-b]',
        'test_prints[myfix-2-c]',
        'test_prints[myfix-myfix2-b-0]',
        'test_prints[myfix-myfix2-b--1]',
        'test_prints[myfix-myfix2-c-0]',
        'test_prints[myfix-myfix2-c--1]',
        'test_prints[myfix-myfix-b]',
        'test_prints[myfix-myfix-c]',
        'test_prints[my_tuple-d-3]',  # val0 in pytest, but we could do better
        'test_prints[my_tuple-e-4]'   # val1
    ]
