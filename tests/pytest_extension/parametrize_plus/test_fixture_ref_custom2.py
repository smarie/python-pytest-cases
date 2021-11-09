# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import parametrize, fixture_ref


has_pytest_param = hasattr(pytest, 'param')


# pytest.param is not available in all versions
if has_pytest_param:
    @pytest.fixture
    def a():
        return 'a'


    @pytest.fixture
    def b():
        return 'b'


    @parametrize('arg', [pytest.param("a", marks=pytest.mark.skipif("5>4")),
                              fixture_ref(b)])
    def test_mark(arg):
        assert arg in ['a', 'b']


    @parametrize('arg', [pytest.param("a", id="testID"),
                              fixture_ref(b)])
    def test_id(arg):
        assert arg in ['a', 'b']


    def test_synthesis(module_results_dct):
        # make sure the id and skip mark were taken into account
        assert list(module_results_dct) == [
            'test_mark[b]',
            'test_id[testID]',
            'test_id[b]'
        ]
