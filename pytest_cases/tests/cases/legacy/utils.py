# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
def nb_pytest_parameters(f):
    """
    Decorator for pytest if f is a pytestmark.

    Args:
        f: (todo): write your description
    """
    try:
        # new pytest
        return len(f.pytestmark)
    except AttributeError:
        # old pytest
        return len(f.parametrize.args) / 2


def get_pytest_param(f, i):
    """
    Get pytestmark parameter.

    Args:
        f: (todo): write your description
        i: (todo): write your description
    """
    try:
        # new pytest
        return f.pytestmark[i].args
    except AttributeError:
        # old pytest
        return f.parametrize.args[2*i:2*(i+1)]
