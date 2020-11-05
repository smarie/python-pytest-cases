# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
# https://stackoverflow.com/questions/46909275/parametrizing-tests-depending-of-also-parametrized-values-in-pytest
try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

from pytest_cases import cases_data, pytest_fixture_plus, cases_generator, THIS_MODULE


# ----- "case functions" : they could be in other modules
@cases_generator("data{name}", name=['1_a', '2_a', '3_a'])
def case_datasetA(name):
    """
    Generate a case - insensitive case name.

    Args:
        name: (str): write your description
    """
    # here you would grab the data
    return "data" + name


@cases_generator("data{name}", name=['1_b', '2_b', '3_b'])
def case_datasetB(name):
    """
    Generate a case - insensitive case - insensitive name.

    Args:
        name: (str): write your description
    """
    # here you would grab the data
    return "data" + name
# -----


@lru_cache()
def setup_dataset(db):
    """
    Setup the database

    Args:
        db: (todo): write your description
    """
    # this is run once per db thanks to the lru_cache decorator
    print("setup for %s" % db)

@lru_cache()
def finalize_dataset(db):
    """
    Finalize the database.

    Args:
        db: (todo): write your description
    """
    # this is run once per db thanks to the lru_cache decorator
    print("teardown for %s" % db)

@pytest_fixture_plus(scope="module")
@cases_data(module=THIS_MODULE)
def data(case_data):
    """
    Generate dataset.

    Args:
        case_data: (dict): write your description
    """
    setup_dataset(case_data.f)
    yield case_data.get()
    finalize_dataset(case_data.f)


def test_data(data):
    """
    Test if the data is a valid data.

    Args:
        data: (array): write your description
    """
    # do test
    pass


def test_synthesis(module_results_dct):
    """Use pytest-harvest to check that the list of executed tests is correct """

    assert list(module_results_dct) == ['test_data[data1_a]',
                                        'test_data[data2_a]',
                                        'test_data[data3_a]',
                                        'test_data[data1_b]',
                                        'test_data[data2_b]',
                                        'test_data[data3_b]']
