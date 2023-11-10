from pytest_cases import parametrize


@parametrize(arg=(1,))
def case_parametrized(arg):
    return arg
