# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

used = False


@pytest.fixture(autouse=True)
def one():
    global used
    used = True
    pass


@pytest.fixture(params=[1, 2])
def two():
    pass


def test_me(two):
    global used
    assert used
