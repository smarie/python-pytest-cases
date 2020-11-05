# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases.fixture_core1_unions import InvalidParamsList
from pytest_cases import parametrize_plus, fixture_ref


@pytest.fixture
def test():
    """
    The test test.

    Args:
    """
    return ['a', 'b', 'c']


def test_invalid_argvalues():
    """
    Validate the test values.

    Args:
    """
    with pytest.raises(InvalidParamsList):
        @parametrize_plus('main_msg', fixture_ref(test))
        def test_prints(main_msg):
            """
            Prints the main test.

            Args:
                main_msg: (str): write your description
            """
            print(main_msg)
