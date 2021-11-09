from pytest_steps import test_steps

from pytest_cases import parametrize, fixture, lazy_value


@fixture
def fix():
    return 1


@fixture
def fixtuple():
    return 1, 2


def foo():
    return 2


def footuple():
    return 3, 4


@test_steps("step1", "step2")
@parametrize("b,c", [fixtuple, lazy_value(footuple)])
@parametrize(a=[fix, lazy_value(foo)])
def test_steps_and_cases(a, b, c):

    print("step 1")
    assert a in (1, 2)
    assert (b, c) in ((1, 2), (3, 4))
    yield

    print("step 2")
    assert a in (1, 2)
    assert (b, c) in ((1, 2), (3, 4))
    yield


@test_steps("step1", "step2")
@parametrize("b,c", [lazy_value(footuple)])  # no fixture ref: only lazy
@parametrize(a=[lazy_value(foo)])            # no fixture ref: only lazy
def test_steps_and_cases2(a, b, c):

    print("step 1")
    assert a in (1, 2)
    assert (b, c) in ((1, 2), (3, 4))
    yield

    print("step 2")
    assert a in (1, 2)
    assert (b, c) in ((1, 2), (3, 4))
    yield
