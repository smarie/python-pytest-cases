# from pytest_cases import parametrize, fixture, fixture_ref
#
#
# @parametrize("a", [1])
# def test_without_fixture_ref(request, a):
#     assert request.getfixturevalue('a') == 1
#
#
# @fixture
# def some_fixture():
#     return 1
#
#
# @parametrize("a", [fixture_ref(some_fixture)])
# def test_with_fixture_ref(request, a):
#     assert request.getfixturevalue('a') == 1
