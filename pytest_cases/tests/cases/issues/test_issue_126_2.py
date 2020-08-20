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
            'test_foo_nested[o_is_a_]',
            'test_foo_nested[o_is_b_-a=*]',
            'test_foo_nested[o_is_b_-a=**]',
            'test_foo_nested[o_is_a__]',
            'test_foo_nested[o_is_b__-a=*]',
            'test_foo_nested[o_is_b__-a=**]',
            'test_foo_nested2[o_is_a_]',      # <- note that case fixture names are the same: correctly reused
            'test_foo_nested2[o_is_b_-a=*]',
            'test_foo_nested2[o_is_b_-a=**]',
            'test_foo_nested2[o_is_a__]',
            'test_foo_nested2[o_is_b__-a=*]',
            'test_foo_nested2[o_is_b__-a=**]',
            # all tests in the module
            'test_bar',
            'test_foo[o_is_a_]',
            'test_foo[o_is_b_-a=*]',
            'test_foo[o_is_b_-a=**]',
            'test_foo[o_is_a__]',
            'test_foo[o_is_b__-a=*]',
            'test_foo[o_is_b__-a=**]',
            'test_foo2[o_is_a_]',  # <- note that case fixture names are the same: correctly reused
            'test_foo2[o_is_b_-a=*]',
            'test_foo2[o_is_b_-a=**]',
            'test_foo2[o_is_a__]',
            'test_foo2[o_is_b__-a=*]',
            'test_foo2[o_is_b__-a=**]'
        ]
