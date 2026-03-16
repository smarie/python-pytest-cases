# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
"""
This is a copy of test at https://github.com/pytest-dev/pytest/blob/master/testing/acceptance_test.py
"""
import pytest

data = {}


@pytest.fixture(scope='module')
def clean_data():
    data.clear()


@pytest.fixture(autouse=True)
def add_data():
    data.update(value=True)


@pytest.mark.usefixtures('clean_data')
def test_value():
    assert data.get('value')
