import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize('a', [0])
async def test_x(a):
    assert True
