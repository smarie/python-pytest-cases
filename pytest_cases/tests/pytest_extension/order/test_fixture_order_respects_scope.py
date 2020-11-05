# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
"""
This is a copy of test at https://github.com/pytest-dev/pytest/blob/master/testing/acceptance_test.py
"""
from distutils.version import LooseVersion

import pytest

data = {}


@pytest.fixture(scope='module')
def clean_data():
    """
    Clean the data.

    Args:
    """
    data.clear()


@pytest.fixture(autouse=True)
def add_data():
    """
    Add data to the list.

    Args:
    """
    data.update(value=True)


@pytest.mark.skipif(LooseVersion(pytest.__version__) < LooseVersion('3.4.0'),
                    reason="This bug was not fixed in old pytest.")
@pytest.mark.usefixtures('clean_data')
def test_value():
    """
    Set the test value

    Args:
    """
    assert data.get('value')
