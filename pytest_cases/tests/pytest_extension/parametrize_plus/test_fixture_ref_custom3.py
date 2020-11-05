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


    @pytest.fixture(params=['r', 't'], ids="b={}".format)
    def b(request):
        """
        Return a string representation of the request.

        Args:
            request: (todo): write your description
        """
        return "b%s" % request.param

    @parametrize_plus('foo', [1,
                              fixture_ref(b),
                              pytest.param('t'),
                              pytest.param('r', id='W'),
                              3,
                              pytest.param(fixture_ref(a)),
                              fixture_ref(a)
                              ], ids=[str(i) for i in range(7)])
    def test_id(foo):
        """
        Returns the id

        Args:
            foo: (todo): write your description
        """
        pass

    def test_synthesis(module_results_dct):
        """
        Test for test results to see if needed.

        Args:
            module_results_dct: (todo): write your description
        """
        # make sure the id and skip mark were taken into account
        assert list(module_results_dct) == [
            'test_id[0]',
            'test_id[1-b=r]',
            'test_id[1-b=t]',
            'test_id[foo_is_P2toP4-2]',
            'test_id[foo_is_P2toP4-W]',
            'test_id[foo_is_P2toP4-4]',
            'test_id[5]',
            'test_id[6]'
        ]
