# META
# {'passed': 10, 'skipped': 0, 'failed': 0}
# END META
import pytest


def test_config(request):
    assert request.session.config.getoption('with_reorder') == 'skip'


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


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_config',
                                        'test[flavor1-vxlan]',
                                        'test[flavor1-vlan]',
                                        'test[flavor2-vxlan]',
                                        'test[flavor2-vlan]',
                                        'test2[flavor1-vxlan]',
                                        'test2[flavor1-vlan]',
                                        'test2[flavor2-vxlan]',
                                        'test2[flavor2-vlan]']
