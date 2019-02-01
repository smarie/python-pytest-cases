from distutils.version import LooseVersion
from itertools import product

import pytest

from pytest_cases import pytest_fixture_plus


STEREO_PATHS = ['stereo 1.wav', 'stereo 2.wav']
CFG_TYPES = [list, dict]


class StateAsserter:
    def __init__(self):
        self.current_state = 0

    def assert_state_and_move(self, path, cfg_factory):
        assert path == STEREO_PATHS[self.current_state % 2]
        assert cfg_factory == CFG_TYPES[(self.current_state // 2)]
        self.current_state += 1


if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
    a = StateAsserter()
else:
    # for old versions of pytest, the execution order seems harder to get strictly
    class UnOrderedStateAsserter:
        def __init__(self):
            self.all_remaining = list(product(STEREO_PATHS, CFG_TYPES))

        def assert_state_and_move(self, path, cfg_factory):
            # just check that this state has not been reached yet and remove it
            self.all_remaining.remove((path, cfg_factory))

    a = UnOrderedStateAsserter()


@pytest_fixture_plus
@pytest.mark.parametrize("path", STEREO_PATHS)
@pytest.mark.parametrize("cfg_factory", CFG_TYPES)   # not actual params
def stereo_cfg(path, cfg_factory, request):
    """
    A fixture with two parameters.

    As opposed to `stereo_cfg_2`, we use here two @parametrize decorators.
    We check that the execution order is correct.
    """
    assert isinstance(path, str)
    assert isinstance(cfg_factory, type)
    a.assert_state_and_move(path=path, cfg_factory=cfg_factory)
    return "hello"


def test_stereo_two_parametrizers(stereo_cfg):
    """
    A test relying on a double-parametrized fixture.
    See https://github.com/pytest-dev/pytest/issues/3960
    """
    pass


# -----------------------------

b = StateAsserter()


@pytest.mark.parametrize("path", STEREO_PATHS)
@pytest.mark.parametrize("cfg_factory", CFG_TYPES)   # not actual params
def test_reference_test(path, cfg_factory, request):
    # a reference test, just to check (visually :) ) that the order of parameterized executions is the same
    b.assert_state_and_move(path=path, cfg_factory=cfg_factory)


# ----------------------------

c = StateAsserter()


def _id(x):
    cfg_factory, path = x
    return "{cfg_factory}-{path}".format(path=path, cfg_factory=cfg_factory.__name__)


@pytest_fixture_plus(scope='module')
@pytest.mark.parametrize("cfg_factory,path", product(CFG_TYPES, STEREO_PATHS), ids=_id)
def stereo_cfg_2(path, request, cfg_factory):
    """
    A fixture with two parameters.

    As opposed to `stereo_cfg_1`, the order of the parameter is precomputed beforehand in
    `product(CFG_TYPES, STEREO_PATHS)` and a single call to parametrize is made.
    We check that the execution order is the same.
    """
    assert isinstance(path, str)
    assert isinstance(cfg_factory, type)

    c.assert_state_and_move(path=path, cfg_factory=cfg_factory)

    yield "hello"


def test_stereo_one_global_parametrizer(stereo_cfg_2):
    pass


# the following works but the order is "optimized" by pytest, making it quite hard to validate by human eye.
# Disabling it for now.
#
# def test_double_stereo(stereo_cfg, stereo_cfg_2):
#     pass
