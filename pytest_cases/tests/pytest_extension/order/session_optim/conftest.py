# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest


def pytest_configure(config):
    class DynamicFixturePlugin(object):
        @pytest.fixture(scope='session', params=['flavor1', 'flavor2'], autouse=False)
        def flavor(self, request):
            print('flavor created:', request.param)
            return request.param

    config.pluginmanager.register(DynamicFixturePlugin(), 'flavor-fixture')
