# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
# https://stackoverflow.com/questions/46909275/parametrizing-tests-depending-of-also-parametrized-values-in-pytest
import pytest

from pytest_cases import parametrize, fixture, fixture_ref

datasets_contents = {
    'datasetA': ['data1_a', 'data2_a', 'data3_a'],
    'datasetB': ['data1_b', 'data2_b', 'data3_b']
}

DA = None

@fixture(scope="module")
def datasetA():
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


@fixture(scope="module")
@pytest.mark.parametrize('data_index', range(len(datasets_contents['datasetA'])), ids="idx={}".format)
def data_from_datasetA(datasetA, data_index):
    assert datasetA == 'DA'
    return datasets_contents['datasetA'][data_index]


DB = None


@fixture(scope="module")
def datasetB():
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


@fixture(scope="module")
@pytest.mark.parametrize('data_index', range(len(datasets_contents['datasetB'])), ids="idx={}".format)
def data_from_datasetB(datasetB, data_index):
    assert datasetB == 'DB'
    return datasets_contents['datasetB'][data_index]


@parametrize('data', [fixture_ref('data_from_datasetA'),
                                  fixture_ref('data_from_datasetB')])
def test_databases(data):
    # do test
    print(data)
