# --- This test is valid but it requires asyncio which is not guaranteed to always be ok with the version of python/pytest in travis.
# For this reason I'll leave it commented for now, maybe one day we'll create a dedicated travis config for things like this

# import random
# import pytest
# from pytest_cases import parametrize_with_cases
#
#
# def sum(a, b):
#     return a + b
#
#
# @pytest.fixture
# def random_num():
#     return random.randint(0, 65543)
#
#
# def case_1(random_num: int):
#     return 1, random_num, 1 + random_num
#
#
# def case_2(random_num: int):
#     return 2, random_num, 2 + random_num
#
#
# @pytest.mark.asyncio
# @parametrize_with_cases('case', cases='.')
# async def test_sum_of(case):
#     a, b, c = case
#     assert sum(a, b) == c
