# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases, fixture


class Cases:

    def case_one(self, bird):
        """
        Return the first result of one result.

        Args:
            self: (todo): write your description
            bird: (todo): write your description
        """
        return "one"

    def case_two(self):
        """
        Returns the number of two - two - case.

        Args:
            self: (todo): write your description
        """
        return "two"


@parametrize_with_cases("v", cases=Cases)
def test_this_is_failing(v):
    """
    Determine whether v is a test.

    Args:
        v: (todo): write your description
    """
    assert v in ["one", "two"]


@fixture
def bird():
    """
    Returns the ] list ]

    Args:
    """
    return "one_proud_bird"
