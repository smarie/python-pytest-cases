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
        """
        Return the b ( b.

        Args:
        """
        return -1


    @pytest.fixture(name='a')
    def a_in_module():
        """
        A module that returns the module

        Args:
        """
        return 1


    class TestA:
        @pytest.fixture(name='a')
        def a_nested(self):
            """
            Return a list of nested list of the two lists.

            Args:
                self: (todo): write your description
            """
            return 2

        def test_a_nested(self, a):
            """
            Test if a is not_a.

            Args:
                self: (todo): write your description
                a: (array): write your description
            """
            assert a == 2

        @parametrize_with_cases('o', debug=True)
        def test_foo_nested(self, o):
            """
            !

            Args:
                self: (todo): write your description
                o: (todo): write your description
            """
            assert o == 'case!'

        @parametrize_with_cases('o', debug=True)
        def test_foo_nested2(self, o):
            """
            !

            Args:
                self: (todo): write your description
                o: (todo): write your description
            """
            assert o == 'case!'


    def test_bar(a):
        """
        Test if a is a bar.

        Args:
            a: (todo): write your description
        """
        assert a == 1


    @parametrize_with_cases('o', debug=True)
    def test_foo(o):
        """
        !

        Args:
            o: (todo): write your description
        """
        assert o == 'case!'


    @parametrize_with_cases('o', debug=True)
    def test_foo2(o):
        """
        !

        Args:
            o: (todo): write your description
        """
        assert o == 'case!'

    def test_synthesis(module_results_dct):
        """
        Synthesis results.

        Args:
            module_results_dct: (todo): write your description
        """
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
