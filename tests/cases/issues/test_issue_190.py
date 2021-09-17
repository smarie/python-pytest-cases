# import functools
#
# from pytest_cases import parametrize_with_cases, case
#
#
# class CasesFeature:
#     @case(tags=("basic",))
#     def case_basic(self):
#         return 0
#
#
# def release_scope(*scopes):
#     if len(scopes) == 0:
#         scopes = ["function"]
#
#     def decorator(f):
#         @functools.wraps(f)
#         def wrapper(case, *args, **kw):
#             f(case, *args, **kw)
#
#         return wrapper
#
#     return decorator
#
#
# @parametrize_with_cases("case", cases=CasesFeature, has_tag="basic", scope="session")
# @release_scope()
# def test_container(case):
#     pass
