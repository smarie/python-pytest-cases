import pytest_cases


def case_tup():
    return [], {}  # This can be reproduced with any mutable object


@pytest_cases.fixture(scope="function")
@pytest_cases.parametrize_with_cases("obj1, obj2", cases=".")
def tup(obj1, obj2):
    return obj1, obj2


def test_1(tup):
    obj1, obj2 = tup

    assert len(obj1) == 0

    obj1.append(1)


def test_2(tup):
    obj1, obj2 = tup

    assert len(obj1) == 0

    obj1.append(1)
