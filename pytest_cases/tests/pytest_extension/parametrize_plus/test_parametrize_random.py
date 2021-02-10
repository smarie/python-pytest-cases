from pytest_cases import parametrize_random


@parametrize_random(value=list(range(8)), size=3)
def test_parametrize_random(value):
    print(value)
