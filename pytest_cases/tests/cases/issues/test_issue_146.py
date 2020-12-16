# from pytest_cases import parametrize_with_cases, fixture
#
#
# def case_without_fixture():
#     important_value = 1
#     other_important_value = 2
#     return important_value, other_important_value
#
#
# @parametrize_with_cases("important_value,other_important_value", cases='.')
# def test_case_without_fixture(request, important_value, other_important_value):
#     # important_value and other_important_value are here no problem
#     value = request.getfixturevalue('important_value').get(request)
#
#     assert value == 1
#     assert other_important_value == 2
#
#
# @fixture
# def some_fixture():
#     return 1
#
#
# def case_with_fixture(some_fixture):
#     important_value = some_fixture
#     other_important_value = 2
#     return important_value, other_important_value
#
#
# @parametrize_with_cases("important_value,other_important_value", cases='.')
# def test_case_with_fixture(request, important_value, other_important_value):
#
#     value = request.getfixturevalue('important_value').get(request)
#     assert value == important_value
#     assert important_value == 1
#     assert other_important_value == 2
