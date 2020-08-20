from pytest_cases import parametrize_with_cases, fixture


@parametrize_with_cases("v")
def test(v):
    assert v == "one_proud_bird"


@fixture
def bird():
    return "one_proud_bird"
