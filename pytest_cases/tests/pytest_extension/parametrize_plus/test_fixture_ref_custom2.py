# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import parametrize_plus, fixture_ref


has_pytest_param = hasattr(pytest, 'param')


# pytest.param is not available in all versions
if has_pytest_param:
    @pytest.fixture
    def a():
        """
        Æł¥åıĸè½¬¦ä¸ĭ¶æģģ

        Args:
        """
        return 'a'


    @pytest.fixture
    def b():
        """
        Returns a string representation of a b.

        Args:
        """
        return 'b'


    @parametrize_plus('arg', [pytest.param("a", marks=pytest.mark.skipif("5>4")),
                              fixture_ref(b)])
    def test_mark(arg):
        """
        Makes sure that the test exists.

        Args:
            arg: (todo): write your description
        """
        assert arg in ['a', 'b']


    @parametrize_plus('arg', [pytest.param("a", id="testID"),
                              fixture_ref(b)])
    def test_id(arg):
        """
        Test if the test test id.

        Args:
            arg: (todo): write your description
        """
        assert arg in ['a', 'b']


    def test_synthesis(module_results_dct):
        """
        Test for test_results.

        Args:
            module_results_dct: (todo): write your description
        """
        # make sure the id and skip mark were taken into account
        assert list(module_results_dct) == [
            'test_mark[arg_is_b]',
            'test_id[testID]',
            'test_id[arg_is_b]'
        ]
