import pytest
from pytest_cases import pytest_parametrize_plus, fixture_ref, pytest_fixture_plus


@pytest_fixture_plus
@pytest.mark.parametrize('val', ['b', 'c'])
def myfix(val):
    return val


@pytest_fixture_plus
@pytest.mark.parametrize('val', [0, -1])
def myfix2(val):
    return val


@pytest_fixture_plus
@pytest.mark.parametrize('val', [('d', 3),
                                 ('e', 4)])
def my_tuple(val):
    return val


@pytest_parametrize_plus('p,q', [('a', 1),
                                 (fixture_ref(myfix), 2),
                                 (fixture_ref(myfix), fixture_ref(myfix2)),
                                 (fixture_ref(myfix), fixture_ref(myfix)),
                                 fixture_ref(my_tuple)])
def test_prints(p, q):
    print(p, q)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_prints[p_q_is_0-a-1]',
                                        'test_prints[p_q_is_fixtureproduct__1-b]',
                                        'test_prints[p_q_is_fixtureproduct__1-c]',
                                        'test_prints[p_q_is_fixtureproduct__2-b-0]',
                                        'test_prints[p_q_is_fixtureproduct__2-b--1]',
                                        'test_prints[p_q_is_fixtureproduct__2-c-0]',
                                        'test_prints[p_q_is_fixtureproduct__2-c--1]',
                                        'test_prints[p_q_is_fixtureproduct__3-b]',
                                        'test_prints[p_q_is_fixtureproduct__3-c]',
                                        "test_prints[p_q_is_my_tuple-('d', 3)]",
                                        "test_prints[p_q_is_my_tuple-('e', 4)]"
                                        ]
