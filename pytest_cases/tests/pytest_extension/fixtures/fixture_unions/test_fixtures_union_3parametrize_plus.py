# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import fixture_union


@pytest.fixture(params=[2, 3])
def a():
    """
    Æł¥åıĸè½¬¦ä¸ĭ¶æģģ

    Args:
    """
    return 'a123'


@pytest.fixture(params=[0, 1, 2])
def b():
    """
    Returns a string representation of a b.

    Args:
    """
    return 'b321'


f_union = fixture_union("f_union", [a, "b"])


def test_fixture_union(f_union):
    """
    Returns a union of union union.

    Args:
        f_union: (todo): write your description
    """
    return
