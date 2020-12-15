# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases.common_pytest_marks import PYTEST3_OR_GREATER, PYTEST361_36X


def test_config(request):
    assert request.session.config.getoption('with_reorder') == 'normal'


@pytest.fixture(scope='session', params=['vxlan', 'vlan'])
def encap(request):
    print('encap created:', request.param)
    return request.param


@pytest.fixture(scope='session')  # autouse='True'
def reprovision(request, flavor, encap):
    print('reprovision created:', flavor, encap)


def test(reprovision):
    pass


def test2(reprovision):
    pass


@pytest.mark.skipif((not PYTEST3_OR_GREATER) or PYTEST361_36X,
                    reason="This 'optimal order' was changed in some versions of pytest")
def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_config',
                                        'test[flavor1-vxlan]',
                                        'test2[flavor1-vxlan]',
                                        'test[flavor2-vxlan]',
                                        'test2[flavor2-vxlan]',
                                        'test[flavor2-vlan]',
                                        'test2[flavor2-vlan]',
                                        'test[flavor1-vlan]',
                                        'test2[flavor1-vlan]']