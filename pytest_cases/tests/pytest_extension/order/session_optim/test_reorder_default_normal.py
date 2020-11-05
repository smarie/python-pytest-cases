# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from distutils.version import LooseVersion

import pytest


def test_config(request):
    """
    Set test configuration.

    Args:
        request: (todo): write your description
    """
    assert request.session.config.getoption('with_reorder') == 'normal'


@pytest.fixture(scope='session', params=['vxlan', 'vlan'])
def encap(request):
    """
    Encap a request.

    Args:
        request: (todo): write your description
    """
    print('encap created:', request.param)
    return request.param


@pytest.fixture(scope='session')  # autouse='True'
def reprovision(request, flavor, encap):
    """
    Reproprovision a revision.

    Args:
        request: (todo): write your description
        flavor: (todo): write your description
        encap: (todo): write your description
    """
    print('reprovision created:', flavor, encap)


def test(reprovision):
    """
    Test if the given revision exists.

    Args:
        reprovision: (bool): write your description
    """
    pass


def test2(reprovision):
    """
    Determine the current working directory.

    Args:
        reprovision: (str): write your description
    """
    pass


@pytest.mark.skipif(LooseVersion(pytest.__version__) < LooseVersion('3.0.0') or
                    LooseVersion('3.6.0') < LooseVersion(pytest.__version__) < LooseVersion('3.7.0'),
                    reason="This 'optimal order' was changed in some versions of pytest")
def test_synthesis(module_results_dct):
    """
    Convert a test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_config',
                                        'test[flavor1-vxlan]',
                                        'test2[flavor1-vxlan]',
                                        'test[flavor2-vxlan]',
                                        'test2[flavor2-vxlan]',
                                        'test[flavor2-vlan]',
                                        'test2[flavor2-vlan]',
                                        'test[flavor1-vlan]',
                                        'test2[flavor1-vlan]']