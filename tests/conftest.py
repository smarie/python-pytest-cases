# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest


pytest_plugins = ["pytester"]
# In order to run meta-tests, see https://docs.pytest.org/en/latest/writing_plugins.html


@pytest.fixture(scope='session', autouse=True)
def environment():
    """For some reason an 'environment' fixture appears in travis CI whil it is not present on local builds.
    I create one here so that fixture closures look identical"""
    pass


@pytest.fixture
def global_fixture():
    return 'global'
