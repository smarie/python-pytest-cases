# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import pytest_parametrize_plus, pytest_fixture_plus, fixture_ref

# ------ Dataset A
DA = ['data1_a', 'data2_a', 'data3_a']
DA_data_indices = list(range(len(DA)))

@pytest_fixture_plus(scope="module")
def datasetA():
    """
    Yields all datasets.

    Args:
    """
    print("setting up dataset A")
    yield DA
    print("tearing down dataset A")

@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize('data_index', DA_data_indices, ids="idx={}".format)
def data_from_datasetA(datasetA, data_index):
    """
    Convert data_dataset.

    Args:
        datasetA: (todo): write your description
        data_index: (todo): write your description
    """
    return datasetA[data_index]

# ------ Dataset B
DB = ['data1_b', 'data2_b']
DB_data_indices = list(range(len(DB)))

@pytest_fixture_plus(scope="module")
def datasetB():
    """
    Dataset dataset

    Args:
    """
    print("setting up dataset B")
    yield DB
    print("tearing down dataset B")

@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize('data_index', range(len(DB)), ids="idx={}".format)
def data_from_datasetB(datasetB, data_index):
    """
    Convert dataset from a dataset

    Args:
        datasetB: (todo): write your description
        data_index: (todo): write your description
    """
    return datasetB[data_index]

# ------ Test

@pytest_parametrize_plus('data', [fixture_ref('data_from_datasetA'),
                                  fixture_ref('data_from_datasetB')])
def test_databases(data):
    """
    Test if the given data.

    Args:
        data: (array): write your description
    """
    # do test
    print(data)
