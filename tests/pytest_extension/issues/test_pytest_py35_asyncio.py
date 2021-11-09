# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize('a', [0])
async def test_x(a):
    assert True
