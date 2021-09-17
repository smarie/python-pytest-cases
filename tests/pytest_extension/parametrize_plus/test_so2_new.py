# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases, parametrize, fixture

datasetA = [10, 20, 30]
dbA_keys = range(3)
dbA_setup = False

datasetB = [100, 200]  # just to see that it works with different sizes :)
dbB_keys = range(2)
dbB_setup = False


@fixture(scope="module")
def dbA():
    #do setup
    global dbA_setup
    assert not dbA_setup
    dbA_setup = True
    yield datasetA
    #finalize


@parametrize(idx=dbA_keys)
def item_from_A(dbA, idx):
    yield dbA[idx]


@fixture(scope="module")
def dbB():
    #do setup
    global dbB_setup
    assert not dbB_setup
    dbB_setup = True
    yield datasetB
    #finalize


@parametrize(idx=dbB_keys)
def item_from_B(dbB, idx):
    yield dbB[idx]


@parametrize_with_cases('data', prefix='item_', cases='.')
def test_data(data):
    print(data)
    #do test
