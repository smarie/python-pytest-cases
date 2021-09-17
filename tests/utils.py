# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases.common_pytest_marks import has_pytest_param


if has_pytest_param:
    def skip(*argvals):
        return pytest.param(*argvals, marks=pytest.mark.skip)
else:
    def skip(*argvals):
        if len(argvals) > 1:
            # we have to keep the tuple
            return pytest.mark.skip(argvals)
        else:
            return pytest.mark.skip(*argvals)
