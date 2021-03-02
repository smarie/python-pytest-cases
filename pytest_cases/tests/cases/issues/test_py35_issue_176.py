import random
import pytest
from pytest_cases import parametrize_with_cases


def sum(a, b):
    return a + b


@pytest.fixture
def random_num():
    return random.randint(0, 65543)


def case_1(random_num: int):
    return 1, random_num, 1 + random_num


def case_2(random_num: int):
    return 2, random_num, 2 + random_num


@pytest.mark.asyncio
@parametrize_with_cases('case', cases='.')
async def test_sum_of(case):
    a, b, c = case
    assert sum(a, b) == c


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        "test_sum_of[1]",
        "test_sum_of[2]"
    ]
