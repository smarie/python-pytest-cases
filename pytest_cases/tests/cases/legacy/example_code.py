# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
try:
    from math import isfinite
except ImportError:
    from math import isnan, isinf

    def isfinite(x):
        """
        isfinite(x) -> bool

        Return True if x is neither an infinity nor a NaN, and False otherwise.
        """
        return not (isinf(x) or isnan(x))


class InfiniteInput(Exception):
    """
    An example exception for which the instances can be compared
    """

    def __init__(self, name):
        """
        Initialize an input.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        super(InfiniteInput, self).__init__(name)

    def __eq__(self, other):
        """
        Determine if two arguments are equal.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        return self.args == other.args


def super_function_i_want_to_test(a, b):
    """
    An example function to be tested
    :param a:
    :param b:
    :return:
    """
    if not isfinite(a):
        raise InfiniteInput('a')
    if not isfinite(b):
        raise InfiniteInput('b')

    return a + 1, b + 1


def super_function_i_want_to_test2(a, b):
    """
    An example function to be tested
    :param a:
    :param b:
    :return:
    """
    if not isfinite(a):
        raise InfiniteInput('a')
    if not isfinite(b):
        raise InfiniteInput('b')

    return a + 1, b + 1
