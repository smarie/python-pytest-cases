import pytest
from pytest_cases import parametrize, parametrize_with_cases


@parametrize(i=range(2), idgen="i=={i}")
def case_i(i):
    return i + 1


@pytest.mark.parametrize('i', range(2), ids="i=={}".format)
def case_k(i):
    return i + 1


@parametrize_with_cases(argnames="j", cases='.')
def test_me(j):
    assert j > 0


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_me[i-i==0]',
        'test_me[i-i==1]',
        'test_me[k-i==0]',
        'test_me[k-i==1]',
    ]
