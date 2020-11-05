# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
#
# In this test we make sure that a session-scoped fixture is setup only once even if it is
# not used in all test nodes because one parametrized test (TestFoo.test_b) requires a fixture union where
# it is not always used.
from pytest_cases import fixture, fixture_ref, parametrize

fa_used = False


@fixture(scope='session')
def fa(request):
    """
    Decorator to set of the current request.

    Args:
        request: (todo): write your description
    """
    global fa_used
    assert not fa_used
    fa_used = True
    return


@fixture(scope='session')
def fb():
    """
    Decorator that can be used asn1.

    Args:
    """
    return


class TestFoo:
    def test_a(self, fa):
        """
        Test if the test is a test.

        Args:
            self: (todo): write your description
            fa: (int): write your description
        """
        pass

    @parametrize("o", [fixture_ref(fa), fixture_ref(fb), fixture_ref(fa)])
    def test_b(self, o):
        """
        Test if the given python value.

        Args:
            self: (todo): write your description
            o: (array): write your description
        """
        pass

    def test_c(self, fa):
        """
        Test if the test is a valid.

        Args:
            self: (todo): write your description
            fa: (array): write your description
        """
        pass
