def test_pytest_cases_plugin_installed(request):
    """A simple test to make sure that the pytest-case plugin is actually installed. Otherwise some tests wont work"""
    assert request.session._fixturemanager.getfixtureclosure.func.__module__ == 'pytest_cases.plugin'
