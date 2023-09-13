from pytest_cases import fixture, parametrize_with_cases


@fixture
@parametrize_with_cases('arg', cases='cases')
def function_scoped(arg):
    return arg


def test_scope_mismatch(scope_mismatch):
    assert scope_mismatch == 1
