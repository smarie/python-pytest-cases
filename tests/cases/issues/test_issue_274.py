import pytest
from pytest_cases import fixture, parametrize_with_cases


class DataCases:
    def data_dummy(self):
        return 1

    def data_dummy2(self):
        return 1

    @pytest.mark.parametrize("a", [False])
    def data_dummy3(self, a):
        return 1


@fixture
@parametrize_with_cases("dset", cases=DataCases, prefix="data_", debug=True)
def dataset(dset):
    assert dset == 1
    yield dset


def test_foo(dataset):
    assert dataset == 1


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_foo[dummy]',
        'test_foo[dummy2]',
        'test_foo[dummy3-False]',
    ]
