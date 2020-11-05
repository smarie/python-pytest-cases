# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import param_fixture


class MyTester():
    def __init__(self, arg=["var0", "var1"]):
        """
        Initialize the command

        Args:
            self: (todo): write your description
            arg: (todo): write your description
        """
        self.arg = arg
        # self.use_arg_to_init_logging_part()

    def dothis(self):
        """
        Dothis doth

        Args:
            self: (todo): write your description
        """
        print("this")

    def dothat(self):
        """
        Print dt ]

        Args:
            self: (todo): write your description
        """
        print("that")


# create a single parameter fixture
var = param_fixture("var", [['var1', 'var2']], ids=str)


@pytest.fixture
def tester(var):
    """Create tester object"""
    return MyTester(var)


class TestIt:
    """ Tests the answer at
    https://stackoverflow.com/questions/18011902/py-test-pass-a-parameter-to-a-fixture-function/55394178#55394178"""
    def test_tc1(self, tester):
        """
        Test the testter for a test.

        Args:
            self: (todo): write your description
            tester: (todo): write your description
        """
       tester.dothis()
       assert 1
