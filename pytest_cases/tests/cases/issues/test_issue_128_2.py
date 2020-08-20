from pytest_cases import parametrize_with_cases, fixture


class Cases:

    def case_one(self, bird):
        return "one"

    def case_two(self):
        return "two"


@parametrize_with_cases("v", cases=Cases)
def test_this_is_failing(v):
    assert v in ["one", "two"]


@fixture
def bird():
    return "one_proud_bird"
