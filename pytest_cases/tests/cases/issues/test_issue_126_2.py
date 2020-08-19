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

        def test_a(self, a):
            assert a == 2

        @parametrize_with_cases('o', debug=True)
        def test_foo_nested(self, o):
            assert o == 'case!'


    def test_bar(a):
        assert a == 1


    @parametrize_with_cases('o', debug=True)
    def test_foo(o):
        assert o == 'case!'


    def test_synthesis(module_results_dct):
         assert list(module_results_dct) == [
             'test_a',
             'test_foo_nested[o_is_a_]',
             'test_bar',
             'test_foo[o_is_a_]'
        ]
