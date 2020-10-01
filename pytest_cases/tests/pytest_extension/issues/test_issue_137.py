# this test is known to fail.
#
# import pytest
# from pytest_cases import fixture, parametrize, fixture_ref
#
#
# @fixture(scope="module")
# def a():
#     assert False, "a was used !"
#
#
# @fixture(scope="module")
# def b():
#     return "b"
#
#
# @parametrize("fixture", [pytest.param(fixture_ref(b)),
#                          pytest.param(fixture_ref(a), marks=pytest.mark.skipif("1 > 0")),
#                          pytest.param(fixture_ref(b))
#                          ])
# def test(fixture):
#     assert fixture == "b"
