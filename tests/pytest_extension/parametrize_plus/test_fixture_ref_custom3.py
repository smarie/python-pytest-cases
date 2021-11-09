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


    @pytest.fixture(params=['r', 't'], ids="b={}".format)
    def b(request):
        return "b%s" % request.param

    @parametrize('foo', [1,
                              fixture_ref(b),
                              pytest.param('t'),
                              pytest.param('r', id='W'),
                              3,
                              pytest.param(fixture_ref(a)),
                              fixture_ref(a)
                              ], ids=["#%s" % i for i in range(7)])
    def test_id(foo):
        pass

    def test_synthesis(module_results_dct):
        # make sure the id and skip mark were taken into account
        assert list(module_results_dct) == [
            'test_id[#0]',
            'test_id[#1-b=r]',
            'test_id[#1-b=t]',
            'test_id[#2]',
            'test_id[W]',  # <-- custom id: takes precedence over ids
            'test_id[#4]',
            'test_id[#5]',
            'test_id[#6]'
        ]
