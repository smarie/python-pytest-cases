from pytest_cases import fixture, parametrize_with_cases


def case_a():
    return 1


@fixture
@parametrize_with_cases("a", cases=case_a)
def dummy_fixture(a):
    return a + 1
