"""
This is a copy of test at https://github.com/pytest-dev/pytest/blob/master/testing/acceptance_test.py
"""
from distutils.version import LooseVersion

import pytest

data = {}


@pytest.fixture(scope='module')
def clean_data():
    data.clear()


@pytest.fixture(autouse=True)
def add_data():
    data.update(value=True)


@pytest.mark.skipif(LooseVersion(pytest.__version__) < LooseVersion('3.4.0'),
                    reason="This bug was not fixed in old pytest.")
@pytest.mark.usefixtures('clean_data')
def test_value():
    assert data.get('value')
