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
    global fa_used
    assert not fa_used
    fa_used = True
    return


@fixture(scope='session')
def fb():
    return


class TestFoo:
    def test_a(self, fa):
        pass

    @parametrize("o", [fixture_ref(fa), fixture_ref(fb), fixture_ref(fa)])
    def test_b(self, o):
        pass

    def test_c(self, fa):
        pass
