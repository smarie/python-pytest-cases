# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases.common_pytest import has_pytest_param

if has_pytest_param:
    def skip(*argvals):
        """
        Decorator for pytest

        Args:
            argvals: (list): write your description
        """
        return pytest.param(*argvals, marks=pytest.mark.skip)
else:
    def skip(*argvals):
        """
        Decorator to skip the command.

        Args:
            argvals: (list): write your description
        """
        return pytest.mark.skip(argvals)
