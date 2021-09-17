# # Authors: Sylvain MARIE <sylvain.marie@se.com>
# #          + All contributors to <https://github.com/smarie/python-pytest-cases>
# #
# # License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
#
# # From answer at https://stackoverflow.com/a/56602597/7262247
# try:
#     from functools import lru_cache
# except ImportError:
#     from functools32 import lru_cache
#
# from pytest_cases import fixture, parametrize, parametrize_with_cases, THIS_MODULE
#
#
# # ----- "case functions" : they could be in other modules
# @parametrize(name=['1_a', '2_a', '3_a'])
# def case_datasetA(name):
#     # here you would grab the data
#     return "data" + name
#
#
# @parametrize(name=['1_b', '2_b', '3_b'])
# def case_datasetB(name):
#     # here you would grab the data
#     return "data" + name
# # -----
#
#
# @lru_cache()
# def setup_dataset(db):
#     # this is run once per db thanks to the lru_cache decorator
#     print("setup for %s" % db)
#
#
# @lru_cache()
# def finalize_dataset(db):
#     # this is run once per db thanks to the lru_cache decorator
#     print("teardown for %s" % db)
#
#
# @fixture(scope="module")
# @parametrize_with_cases("case_data", cases=THIS_MODULE)
# def data(case_data):
#     setup_dataset(case_data.f)
#     yield case_data
#     finalize_dataset(case_data.f)
#
#
# def test_data(data):
#     # do test
#     pass
#
#
# def test_synthesis(module_results_dct):
#     """Use pytest-harvest to check that the list of executed tests is correct """
#
#     assert list(module_results_dct) == ['test_data[data1_a]',
#                                         'test_data[data2_a]',
#                                         'test_data[data3_a]',
#                                         'test_data[data1_b]',
#                                         'test_data[data2_b]',
#                                         'test_data[data3_b]']
