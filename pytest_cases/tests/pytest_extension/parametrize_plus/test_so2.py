# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
# https://stackoverflow.com/questions/46909275/parametrizing-tests-depending-of-also-parametrized-values-in-pytest
import pytest

from pytest_cases import pytest_parametrize_plus, pytest_fixture_plus, fixture_ref

datasets_contents = {
    'datasetA': ['data1_a', 'data2_a', 'data3_a'],
    'datasetB': ['data1_b', 'data2_b', 'data3_b']
}

DA = None

@pytest_fixture_plus(scope="module")
def datasetA():
    """
    Context manager to the global dataset.

    Args:
    """
    global DA

    # setup the database connection
    print("setting up dataset A")
    assert DA is None
    DA = 'DA'

    yield DA

    # teardown the database connection
    print("tearing down dataset A")
    assert DA == 'DA'
    DA = None


@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize('data_index', range(len(datasets_contents['datasetA'])), ids="idx={}".format)
def data_from_datasetA(datasetA, data_index):
    """
    Return dataset from a dataset. dataset.

    Args:
        datasetA: (todo): write your description
        data_index: (todo): write your description
    """
    assert datasetA == 'DA'
    return datasets_contents['datasetA'][data_index]


DB = None


@pytest_fixture_plus(scope="module")
def datasetB():
    """
    Context manager for global dataset.

    Args:
    """
    global DB

    # setup the database connection
    print("setting up dataset B")
    assert DB is None
    DB = 'DB'

    yield DB

    # teardown the database connection
    print("tearing down dataset B")
    assert DB == 'DB'
    DB = None


@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize('data_index', range(len(datasets_contents['datasetB'])), ids="idx={}".format)
def data_from_datasetB(datasetB, data_index):
    """
    Return dataset from dataset.

    Args:
        datasetB: (todo): write your description
        data_index: (todo): write your description
    """
    assert datasetB == 'DB'
    return datasets_contents['datasetB'][data_index]


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
