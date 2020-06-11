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


    @parametrize_plus('arg1,arg2', [pytest.param("a", 1, id="testID"),
                                    ("b", 1),
                                    (fixture_ref(b), 1),
                                    pytest.param("c", 1, id="testID3"),
                                    pytest.param(fixture_ref(b), 1, id="testID4"),
                                    ("c", 1),
                                    ], debug=True)
    def test_id_tuple(arg1, arg2):
        assert arg1 in ['a', 'b', 'c'] and arg2 == 1


    def test_synthesis(module_results_dct):
        # make sure the id and skip mark were taken into account
        assert list(module_results_dct) == [
            'test_id_tuple[arg1_arg2_is_P0toP1-testID]',
            'test_id_tuple[arg1_arg2_is_P0toP1-b-1]',
            'test_id_tuple[arg1_arg2_is_P2]',
            'test_id_tuple[testID3]',
            'test_id_tuple[testID4]',
            'test_id_tuple[arg1_arg2_is_c-1]',
        ]
