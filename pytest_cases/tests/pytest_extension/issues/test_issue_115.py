# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest


def iterate():
    """
    Iterate over all items of the iterable.

    Args:
    """
    for i in range(10):
        yield i


@pytest.mark.parametrize("idx", iterate())
def test_fn(idx):
    """
    Decorator to run a test function.

    Args:
        idx: (int): write your description
    """
    pass
