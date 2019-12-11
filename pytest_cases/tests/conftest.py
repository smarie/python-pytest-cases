import sys
import pytest


pytest_plugins = ["pytester"]
# In order to run meta-tests, see https://docs.pytest.org/en/latest/writing_plugins.html


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """
    In python 2, add

        --ignore-glob='**/*py35*.py'

    :param config:
    :return:
    """
    if sys.version_info < (3, 5):
        print("Python < 3.5: ignoring test files containing 'py35'")
        OPT = ['**/*py35*.py']
        if config.option.ignore_glob is None:
            config.option.ignore_glob = OPT
        else:
            config.option.ignore_glob += OPT

        # assert config.getoption('--ignore-glob') == OPT


@pytest.fixture
def global_fixture():
    return 'global'
