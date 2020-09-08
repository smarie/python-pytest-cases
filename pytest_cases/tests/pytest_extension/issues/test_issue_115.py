# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest


def iterate():
    for i in range(10):
        yield i


@pytest.mark.parametrize("idx", iterate())
def test_fn(idx):
    pass
