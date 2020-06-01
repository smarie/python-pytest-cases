"""
From https://github.com/smarie/python-pytest-cases/issues/62
"""
from __future__ import unicode_literals
import pytest


@pytest.fixture
def my_cool_fixture():
    return 'hello world'


@pytest.mark.parametrize('object_id', ['a1', 'b2', 'b3'])
def test_my_cool_feature_with_fixture(my_cool_fixture, object_id):
    print(my_cool_fixture)
    print(object_id)
    pass
