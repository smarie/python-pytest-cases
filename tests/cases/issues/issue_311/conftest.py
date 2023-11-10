from pytest_cases import fixture, parametrize_with_cases


@fixture(scope='session')
@parametrize_with_cases('arg', cases='cases', scope='session')
def scope_mismatch(arg):
    return [arg]

session_scoped = scope_mismatch
