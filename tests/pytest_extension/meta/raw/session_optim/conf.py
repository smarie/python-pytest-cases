import pytest

def pytest_configure(config):
    # change the option
    setattr(config.option, 'with_reorder', 'skip')

    # add dynamic fixture
    class DynamicFixturePlugin(object):
        @pytest.fixture(scope='session', params=['flavor1', 'flavor2'], autouse=False)
        def flavor(self, request):
            print('flavor created:', request.param)
            return request.param

    config.pluginmanager.register(DynamicFixturePlugin(), 'flavor-fixture')
