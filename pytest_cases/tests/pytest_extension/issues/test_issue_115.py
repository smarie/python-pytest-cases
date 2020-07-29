import pytest


def iterate():
    for i in range(10):
        yield i


@pytest.mark.parametrize("idx", iterate())
def test_fn(idx):
    pass
