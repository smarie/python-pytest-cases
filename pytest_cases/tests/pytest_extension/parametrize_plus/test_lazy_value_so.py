# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from functools import partial
from random import random

import pytest

from pytest_cases import lazy_value


database = [random() for i in range(10)]


def get_param(i):
    """
    Return the parameter from the value

    Args:
        i: (str): write your description
    """
    return database[i]


def make_param_getter(i, use_partial=True):
    """
    Make a function that will return the value.

    Args:
        i: (todo): write your description
        use_partial: (bool): write your description
    """
    if use_partial:
        return partial(get_param, i)
    else:
        def _get_param():
            """
            Get the value of the database.

            Args:
            """
            return database[i]

        return _get_param


many_parameters = (make_param_getter(i) for i in range(10))


@pytest.mark.parametrize('a', [lazy_value(f) for f in many_parameters])
def test_foo(a):
    """
    Prints out of - b

    Args:
        a: (todo): write your description
    """
    print(a)
