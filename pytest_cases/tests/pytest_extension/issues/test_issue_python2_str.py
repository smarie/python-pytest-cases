# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
"""
From https://github.com/smarie/python-pytest-cases/issues/62
"""
from __future__ import unicode_literals
import pytest


@pytest.fixture
def my_cool_fixture():
    """
    Èi̇·åıĸæīģ¯

    Args:
    """
    return 'hello world'


@pytest.mark.parametrize('object_id', ['a1', 'b2', 'b3'])
def test_my_cool_feature_with_fixture(my_cool_fixture, object_id):
    """
    Prints out the test features for a given feature

    Args:
        my_cool_fixture: (str): write your description
        object_id: (str): write your description
    """
    print(my_cool_fixture)
    print(object_id)
    pass
