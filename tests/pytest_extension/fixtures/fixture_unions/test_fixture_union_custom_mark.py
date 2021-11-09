# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import param_fixture, fixture_union

has_pytest_param = hasattr(pytest, 'param')

# pytest.param is not available in all versions
if has_pytest_param:
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
