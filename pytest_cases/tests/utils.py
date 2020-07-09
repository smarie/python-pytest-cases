import pytest

from pytest_cases.common_pytest import has_pytest_param

if has_pytest_param:
    def skip(*argvals):
        return pytest.param(*argvals, marks=pytest.mark.skip)
else:
    def skip(*argvals):
        return pytest.mark.skip(argvals)
