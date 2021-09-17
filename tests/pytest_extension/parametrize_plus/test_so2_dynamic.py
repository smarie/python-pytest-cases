# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from makefun import with_signature

from pytest_cases import parametrize, fixture, fixture_ref

# ------ Datasets
datasets = {
    'DA': ['data1_a', 'data2_a', 'data3_a'],
    'DB': ['data1_b', 'data2_b']
}
datasets_indices = {dn: range(len(dc)) for dn, dc in datasets.items()}


# ------ Datasets fixture generation
def create_dataset_fixture(dataset_name):
    @fixture(scope="module", name=dataset_name)
    def dataset():
        print("setting up dataset %s" % dataset_name)
        yield datasets[dataset_name]
        print("tearing down dataset %s" % dataset_name)

    return dataset

def create_data_from_dataset_fixture(dataset_name):
    @fixture(name="data_from_%s" % dataset_name, scope="module")
    @pytest.mark.parametrize('data_index', dataset_indices, ids="idx={}".format)
    @with_signature("(%s, data_index)" % dataset_name)
    def data_from_dataset(data_index, **kwargs):
        dataset = kwargs.popitem()[1]
        return dataset[data_index]

    return data_from_dataset

for dataset_name, dataset_indices in datasets_indices.items():
    globals()[dataset_name] = create_dataset_fixture(dataset_name)
    globals()["data_from_%s" % dataset_name] = create_data_from_dataset_fixture(dataset_name)

# ------ Test
@parametrize('data', [fixture_ref('data_from_%s' % n)
                                  for n in datasets_indices.keys()])
def test_databases(data):
    # do test
    print(data)
