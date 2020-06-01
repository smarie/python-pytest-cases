# META
# {'passed': 3, 'skipped': 0, 'failed': 0}
# END META
import pytest


def test_config(request):
    assert request.session.config.getoption('with_reorder') == 'skip'


def test_foo():
    pass


@pytest.mark.black
def test_bar():
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_config',
                                        'test_foo']
