from pytest_cases import pytest_fixture_plus, fixture_union


state = -1


@pytest_fixture_plus
def a(request):
    global state
    assert state == 3
    state = 0
    yield
    state = 1


@pytest_fixture_plus
def b(request):
    global state
    state = 2
    yield
    state = 3


c = fixture_union('c', [b, a])

# @pytest_fixture_plus
# def c(b, a):
#     pass


def test_all(c):
    pass


def test_synthesis():
    assert state == 1
