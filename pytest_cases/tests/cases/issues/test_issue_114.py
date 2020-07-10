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
