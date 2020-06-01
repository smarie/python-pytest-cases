from distutils.version import LooseVersion

import pytest

from pytest_cases import param_fixture, fixture_union

# pytest.param is not available in all versions
if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
    a = param_fixture("a", [1,
                            pytest.param(2, id='22'),
                            pytest.param(3, marks=pytest.mark.skip)
                            ])


    b = param_fixture("b", [3, 4])


    c = fixture_union('c', [pytest.param('a', id='A'),
                            pytest.param(b, marks=pytest.mark.skip)
                            ],
                      ids=['ignored', 'B'],
                      )


    def test_foo(c):
        pass


    def test_synthesis(module_results_dct):
        # TODO most probably the skip mark on b seeems to mess with the union behaviour.
        assert list(module_results_dct) == [
            'test_foo[A-1]',
            'test_foo[A-22]',
        ]
