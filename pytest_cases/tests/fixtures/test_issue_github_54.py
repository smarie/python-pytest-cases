import pytest

from pytest_cases.fixture_core1_unions import InvalidParamsList
from pytest_cases import parametrize_plus, fixture_ref


@pytest.fixture
def test():
    return ['a', 'b', 'c']


def test_invalid_argvalues():
    with pytest.raises(InvalidParamsList):
        @parametrize_plus('main_msg', fixture_ref(test))
        def test_prints(main_msg):
            print(main_msg)
