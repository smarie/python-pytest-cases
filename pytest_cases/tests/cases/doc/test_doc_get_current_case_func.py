# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases


def case_a():
    return 1, 2

def tuplecase_a():
    return 1, 2

def fixturecase_a(request):
    return 1, 2

def fixturetuplecase_a(request):
    return 1, 2


@parametrize_with_cases("f1,f2", cases=fixturetuplecase_a)
@parametrize_with_cases("f", cases=fixturecase_a)
@parametrize_with_cases("t1,t2", cases=tuplecase_a)
@parametrize_with_cases("a", cases=case_a)
def test_a(a, t1, t2, f, f1, f2, current_cases):
    assert current_cases == {
        "a": ("a", case_a),
        "t1": ("tuplecase_a", tuplecase_a),
        "t2": ("tuplecase_a", tuplecase_a),
        "f": ("fixturecase_a", fixturecase_a),
        "f1": ("fixturetuplecase_a", fixturetuplecase_a),
        "f2": ("fixturetuplecase_a", fixturetuplecase_a),
    }
