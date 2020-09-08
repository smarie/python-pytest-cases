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
    return database[i]


def make_param_getter(i, use_partial=True):
    if use_partial:
        return partial(get_param, i)
    else:
        def _get_param():
            return database[i]

        return _get_param


many_parameters = (make_param_getter(i) for i in range(10))


@pytest.mark.parametrize('a', [lazy_value(f) for f in many_parameters])
def test_foo(a):
    print(a)
