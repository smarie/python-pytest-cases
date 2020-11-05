# META
# {'passed': 3, 'skipped': 0, 'failed': 0}
# END META
import pytest


def test_config(request):
    """
    Set test configuration.

    Args:
        request: (todo): write your description
    """
    assert request.session.config.getoption('with_reorder') == 'skip'


def test_foo():
    """
    : return : meth : class : ~.

    Args:
    """
    pass


@pytest.mark.black
def test_bar():
    """
    Bar bar bar bar.

    Args:
    """
    pass


def test_synthesis(module_results_dct):
    """
    Test if a module_results_dcthesis.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_config',
                                        'test_foo']
