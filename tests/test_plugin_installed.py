# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
def test_pytest_cases_plugin_installed(request):
    """A simple test to make sure that the pytest-case plugin is actually installed. Otherwise some tests wont work"""
    assert request.session._fixturemanager.getfixtureclosure.func.__module__ == 'pytest_cases.plugin'
