# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases.common_pytest_marks import has_pytest_param
from pytest_cases import parametrize_with_cases


# only do this for pytest version 3+
if has_pytest_param:
    @pytest.fixture
    def b():
        return -1


    @pytest.fixture(name='a')
    def a_in_module():
        return 1


    class TestA:
        @pytest.fixture(name='a')
        def a_nested(self):
            return 2

        def test_a_nested(self, a):
            assert a == 2

        @parametrize_with_cases('o', debug=True)
        def test_foo_nested(self, o):
            assert o == 'case!'

        @parametrize_with_cases('o', debug=True)
        def test_foo_nested2(self, o):
            assert o == 'case!'


    def test_bar(a):
        assert a == 1


    @parametrize_with_cases('o', debug=True)
    def test_foo(o):
        assert o == 'case!'


    @parametrize_with_cases('o', debug=True)
    def test_foo2(o):
        assert o == 'case!'

    def test_synthesis(module_results_dct):
        assert list(module_results_dct) == [
            # all tests in TestA class
            'test_a_nested',
            # in the test_issue_126_2_cases.py, there are two cases with id "a" and two with id "b"
            'test_foo_nested[a0]',
            'test_foo_nested[b0-a=*]',
            'test_foo_nested[b0-a=**]',
            'test_foo_nested[a1]',
            'test_foo_nested[b1-a=*]',
            'test_foo_nested[b1-a=**]',
            'test_foo_nested2[a0]',      # <- note that case names are the same than above: correctly reused
            'test_foo_nested2[b0-a=*]',
            'test_foo_nested2[b0-a=**]',
            'test_foo_nested2[a1]',
            'test_foo_nested2[b1-a=*]',
            'test_foo_nested2[b1-a=**]',
            # all tests in the module
            'test_bar',
            'test_foo[a0]',
            'test_foo[b0-a=*]',
            'test_foo[b0-a=**]',
            'test_foo[a1]',
            'test_foo[b1-a=*]',
            'test_foo[b1-a=**]',
            'test_foo2[a0]',  # <- note that case fixture names are the same: correctly reused
            'test_foo2[b0-a=*]',
            'test_foo2[b0-a=**]',
            'test_foo2[a1]',
            'test_foo2[b1-a=*]',
            'test_foo2[b1-a=**]'
        ]
