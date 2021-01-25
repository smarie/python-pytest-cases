import pytest_cases as pytest


@pytest.fixture
def db_dep():
    return None


class CaseX:
    def case_one(self, db_dep):
        return 1

    def case_two(self, db_dep):
        return 2


class CaseY:
    @pytest.parametrize_with_cases("x", cases=CaseX, debug=True)
    def case_x_one(self,db_dep,x):
        return x, 1

    @pytest.parametrize_with_cases("x", cases=CaseX, debug=True)
    def case_x_two(self,db_dep,x):
        return x, 1


@pytest.parametrize_with_cases("x,y", cases=CaseY, debug=True)
def test_nested_parametrize(x, y):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_nested_parametrize[x_one-one]',
        'test_nested_parametrize[x_one-two]',
        'test_nested_parametrize[x_two-one]',
        'test_nested_parametrize[x_two-two]'
    ]
