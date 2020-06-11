import pytest
from pytest_cases import parametrize_plus, fixture_ref


has_pytest_param = hasattr(pytest, 'param')


# pytest.param is not available in all versions
if has_pytest_param:
    @pytest.fixture
    def a():
        return 'a'


    @pytest.fixture
    def b():
        return 'b'


    @parametrize_plus('arg', [pytest.param("a", marks=pytest.mark.skipif("5>4")),
                              fixture_ref(b)])
    def test_mark(arg):
        assert arg in ['a', 'b']


    @parametrize_plus('arg', [pytest.param("a", id="testID"),
                              fixture_ref(b)])
    def test_id(arg):
        assert arg in ['a', 'b']


    def test_synthesis(module_results_dct):
        # make sure the id and skip mark were taken into account
        assert list(module_results_dct) == [
            'test_mark[arg_is_b]',
            'test_id[testID]',
            'test_id[arg_is_b]'
        ]
