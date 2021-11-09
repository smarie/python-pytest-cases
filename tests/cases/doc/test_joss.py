# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from random import random
# from tabulate import tabulate
from pytest_cases import parametrize, parametrize_with_cases


def data_a():
    # a simple test case is a function.
    # You can read or generate the data here
    return "<data>"


@parametrize(p=range(2))
def data_b(p):
    # test cases can be easily parametrized
    # and can require fixtures (database connections...)
    return "<data%s>" % p


def algo_a():
    # you can use different prefixes for different *kind* of test cases
    # (algorithms, datasets, users, etc.)
    return 1


@parametrize_with_cases("algo", cases=".", prefix="algo_")
@parametrize_with_cases("data", cases=".", prefix="data_")
def test_evaluation(algo, data, results_bag):
    # you can use results_bag from `pytest_harvest` to collect performance metrics
    # (here you would actually use the algorithm on the data !)
    results_bag.perf = random()


# from tabulate import tabulate
#
# def test_synthesis(module_results_df):
#     # we use this `module_results_df` fixture from `pytest-harvest`
#     # to collect the final results table.
#     print(tabulate(module_results_df, headers="keys"))
