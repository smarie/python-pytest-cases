try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature

import pytest


# Create a symbol that will work to create a fixture containing 'yield', whatever the pytest version
# Note: if more prevision is needed, use    if LooseVersion(pytest.__version__) < LooseVersion('3.0.0')
if int(pytest.__version__.split('.', 1)[0]) < 3:
    yield_fixture = pytest.yield_fixture
else:
    yield_fixture = pytest.fixture


class _LegacyMark:
    __slots__ = "args", "kwargs"

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class _ParametrizationMark:
    """
    Represents the information required by `decorate_pytest_fixture_plus` to work.
    """
    __slots__ = "param_names", "param_values", "param_ids"

    def __init__(self, mark):
        bound = get_parametrize_signature().bind(*mark.args, **mark.kwargs)
        self.param_names = bound.arguments['argnames'].split(',')
        self.param_values = bound.arguments['argvalues']
        try:
            bound.apply_defaults()
            self.param_ids = bound.arguments['ids']
        except AttributeError:
            # can happen if signature is from funcsigs so we have to apply ourselves
            self.param_ids = bound.arguments.get('ids', None)


def get_pytest_parametrize_marks(f):
    """
    Returns the @pytest.mark.parametrize marks associated with a function

    :param f:
    :return: a tuple containing all 'parametrize' marks
    """
    # pytest > 3.2.0
    marks = getattr(f, 'pytestmark', None)
    if marks is not None:
        return tuple(_ParametrizationMark(m) for m in marks if m.name == 'parametrize')
    else:
        # older versions
        mark_info = getattr(f, 'parametrize', None)
        if mark_info is not None:
            # mark_info.args contains a list of (name, values)
            return tuple(_ParametrizationMark(_LegacyMark(mark_info.args[2*i], mark_info.args[2*i + 1],
                                                          **mark_info.kwargs))
                         for i in range(len(mark_info.args) // 2))
        else:
            return ()


def _pytest_mark_parametrize(argnames, argvalues, ids=None):
    """ Fake method to have a reference signature of pytest.mark.parametrize"""
    pass


def get_parametrize_signature():
    """

    :return: a reference signature representing
    """
    return signature(_pytest_mark_parametrize)
