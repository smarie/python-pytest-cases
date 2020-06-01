from distutils.version import LooseVersion

import pytest


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


@pytest.mark.skipif(LooseVersion(pytest.__version__) < LooseVersion('3.0.0') or
                    LooseVersion('3.6.0') < LooseVersion(pytest.__version__) < LooseVersion('3.7.0'),
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