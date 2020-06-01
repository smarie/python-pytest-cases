import pytest
from pytest_cases import param_fixture

has_pytest_param = hasattr(pytest, 'param')

# pytest.param - not available in all versions
if has_pytest_param:
    a = param_fixture("a", [1,
                            pytest.param(2, id='22'),
                            pytest.param(3, marks=pytest.mark.skip)
                            ])


    def test_foo(a):
        pass


    def test_synthesis(module_results_dct):
        # id taken into account as well as skip mark (module_results_dct filters on non-skipped)
        assert list(module_results_dct) == ['test_foo[1]', 'test_foo[22]']
