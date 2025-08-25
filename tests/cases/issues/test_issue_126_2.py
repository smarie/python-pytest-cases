# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
"""
This test file is about chacking that all fixture naming conflicts are handled correctly, between fixtures in the
module, in the test classes, and the fixtures generated for the case functions when they are parametrized or require
fixtures.
"""
import pytest

from pytest_cases.common_pytest_marks import has_pytest_param
from pytest_cases import parametrize_with_cases


# only do this for pytest version 3+
if has_pytest_param:
    @pytest.fixture
    def b():
        """This fixture has the same name as the fixtures created for cases in the test_issue_126_2_cases.py"""
        return -1


    @pytest.fixture(name='a')
    def a_in_module():
        """This fixture has the same name as the fixtures created for cases in the test_issue_126_2_cases.py"""
        return 1


    class TestA:
        @pytest.fixture(name='a')
        def a_nested(self):
            """This fixture has the same name as the fixtures created for cases in the test_issue_126_2_cases.py"""
            return 2

        def test_a_nested(self, a):
            """Here the requested fixture is `a` so it is the one from this file, not the one generated from the case
            file. Since the nested one overrides the module one, it is 2 and not 1"""
            assert a == 2

        @parametrize_with_cases('o', debug=True)
        def test_foo_nested(self, o):
            """
            Here parameter o will receive as argvalues the various cases defined in the test_issue_126_2_cases.py,
            all equal to 'case!'. If it receives "1" or "-1", it means that the fixtures generated for the cases did
            not well manage to coexists with the fixtures in this file, above.
            """
            assert o == 'case!'

        @parametrize_with_cases('o', debug=True)
        def test_foo_nested2(self, o):
            """
            Here parameter o will receive as argvalues the various cases defined in the test_issue_126_2_cases.py,
            all equal to 'case!'. If it receives "1" or "-1", it means that the fixtures generated for the cases did
            not well manage to coexists with the fixtures in this file, above.
            """
            assert o == 'case!'


    def test_bar(a):
        """Here the requested fixture is `a` so it is the one from this file, not the one generated from the case
        file. S it is 1"""
        assert a == 1


    @parametrize_with_cases('o', debug=True)
    def test_foo(o):
        """
        Here parameter o will receive as argvalues the various cases defined in the test_issue_126_2_cases.py,
        all equal to 'case!'. If it receives "1" or "-1", it means that the fixtures generated for the cases did
        not well manage to coexists with the fixtures in this file, above.
        """
        assert o == 'case!'


    @parametrize_with_cases('o', debug=True)
    def test_foo2(o):
        """
        Here parameter o will receive as argvalues the various cases defined in the test_issue_126_2_cases.py,
        all equal to 'case!'. If it receives "1" or "-1", it means that the fixtures generated for the cases did
        not well manage to coexists with the fixtures in this file, above.
        """
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
