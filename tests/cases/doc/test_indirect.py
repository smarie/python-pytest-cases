from pytest_cases import parametrize, fixture


@fixture
@parametrize(a=[0, 1])
def my_fix(a):
    return a * 2


@fixture
@parametrize(b=[0, 10])
def my_fix2(b, my_fix):
    return b + my_fix


def test_foo(my_fix2):
    assert my_fix2 in (0, 2, 10, 12)


@parametrize(my_fix=[2], indirect=True)
def test_foo_indirect(my_fix2):
    assert my_fix2 in (4, 14)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_foo[b=0-a=0]',
        'test_foo[b=0-a=1]',
        'test_foo[b=10-a=0]',
        'test_foo[b=10-a=1]',
        'test_foo_indirect[b=0-my_fix=2]',
        'test_foo_indirect[b=10-my_fix=2]'
    ]
