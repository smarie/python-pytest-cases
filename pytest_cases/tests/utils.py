def nb_pytest_parameters(f):
    try:
        # new pytest
        return len(f.pytestmark)
    except AttributeError:
        # old pytest
        return len(f.parametrize.args) / 2


def get_pytest_param(f, i):
    try:
        # new pytest
        return f.pytestmark[i].args
    except AttributeError:
        # old pytest
        return f.parametrize.args[2*i:2*(i+1)]
