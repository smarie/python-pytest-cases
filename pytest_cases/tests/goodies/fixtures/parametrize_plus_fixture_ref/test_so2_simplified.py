import pytest
from pytest_cases import pytest_parametrize_plus, pytest_fixture_plus, fixture_ref

# ------ Dataset A
DA = ['data1_a', 'data2_a', 'data3_a']
DA_data_indices = list(range(len(DA)))

@pytest_fixture_plus(scope="module")
def datasetA():
    print("setting up dataset A")
    yield DA
    print("tearing down dataset A")

@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize('data_index', DA_data_indices, ids="idx={}".format)
def data_from_datasetA(datasetA, data_index):
    return datasetA[data_index]

# ------ Dataset B
DB = ['data1_b', 'data2_b']
DB_data_indices = list(range(len(DB)))

@pytest_fixture_plus(scope="module")
def datasetB():
    print("setting up dataset B")
    yield DB
    print("tearing down dataset B")

@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize('data_index', range(len(DB)), ids="idx={}".format)
def data_from_datasetB(datasetB, data_index):
    return datasetB[data_index]

# ------ Test

@pytest_parametrize_plus('data', [fixture_ref('data_from_datasetA'),
                                  fixture_ref('data_from_datasetB')])
def test_databases(data):
    # do test
    print(data)
