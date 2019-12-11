import fnmatch
import sys
import pytest
import six

pytest_plugins = ["pytester"]
# In order to run meta-tests, see https://docs.pytest.org/en/latest/writing_plugins.html


def pytest_ignore_collect(path, config):
    """
    In python 2, equivalent of adding

        --ignore-glob='**/*py35*.py'

    This method works even with old pytest 2 and 3.
    It was copied from recent pytest.main.pytest_ignore_collect

    :param path:
    :param config:
    :return:
    """
    if sys.version_info < (3, 5):
        ignore_globs = ['**/*py35*.py']
        if any(
                fnmatch.fnmatch(six.text_type(path), six.text_type(glob))
                for glob in ignore_globs
        ):
            return True


# @pytest.hookimpl(trylast=True)
# def pytest_configure(config):
#     """
#     In python 2, add
#
#         --ignore-glob='**/*py35*.py'
#
#     Unfortunately this is not supported in old pytests so we do this in pytest-collect
#
#     :param config:
#     :return:
#     """
#     if sys.version_info < (3, 5):
#         print("Python < 3.5: ignoring test files containing 'py35'")
#         OPT = ['**/*py35*.py']
#         if config.option.ignore_glob is None:
#             config.option.ignore_glob = OPT
#         else:
#             config.option.ignore_glob += OPT
#
#         assert config.getoption('--ignore-glob') == OPT


@pytest.fixture
def global_fixture():
    return 'global'
