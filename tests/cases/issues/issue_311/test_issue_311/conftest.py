from pytest_cases import fixture, parametrize_with_cases


@fixture(scope='class')
@parametrize_with_cases('arg', cases='cases', scope='class')
def class_scoped(arg):
    return [arg]
