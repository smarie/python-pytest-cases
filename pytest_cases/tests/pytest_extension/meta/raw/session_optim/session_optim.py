# META
# {'passed': 10, 'skipped': 0, 'failed': 0}
# END META
import pytest


def test_config(request):
    """
    Set test configuration.

    Args:
        request: (todo): write your description
    """
    assert request.session.config.getoption('with_reorder') == 'skip'


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


def test_synthesis(module_results_dct):
    """
    Convert a test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_config',
                                        'test[flavor1-vxlan]',
                                        'test[flavor1-vlan]',
                                        'test[flavor2-vxlan]',
                                        'test[flavor2-vlan]',
                                        'test2[flavor1-vxlan]',
                                        'test2[flavor1-vlan]',
                                        'test2[flavor2-vxlan]',
                                        'test2[flavor2-vlan]']
