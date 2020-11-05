# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import warnings
from distutils.version import LooseVersion

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature  # noqa


import pytest

from .common_mini_six import string_types


def get_param_argnames_as_list(argnames):
    """
    pytest parametrize accepts both coma-separated names and list/tuples.
    This function makes sure that we always return a list
    :param argnames:
    :return:
    """
    if isinstance(argnames, string_types):
        argnames = argnames.replace(' ', '').split(',')
    return list(argnames)


# noinspection PyUnusedLocal
def _pytest_mark_parametrize(argnames, argvalues, ids=None, indirect=False, scope=None, **kwargs):
    """ Fake method to have a reference signature of pytest.mark.parametrize"""
    pass


def get_parametrize_signature():
    """

    :return: a reference signature representing
    """
    return signature(_pytest_mark_parametrize)


class _ParametrizationMark:
    """
    Container for the mark information that we grab from the fixtures (`@fixture_plus`)

    Represents the information required by `@fixture_plus` to work.
    """
    __slots__ = "param_names", "param_values", "param_ids"

    def __init__(self, mark):
        """
        Initialize the parameter.

        Args:
            self: (todo): write your description
            mark: (str): write your description
        """
        bound = get_parametrize_signature().bind(*mark.args, **mark.kwargs)
        try:
            remaining_kwargs = bound.arguments['kwargs']
        except KeyError:
            pass
        else:
            if len(remaining_kwargs) > 0:
                warnings.warn("parametrize kwargs not taken into account: %s. Please report it at"
                              " https://github.com/smarie/python-pytest-cases/issues" % remaining_kwargs)
        self.param_names = get_param_argnames_as_list(bound.arguments['argnames'])
        self.param_values = bound.arguments['argvalues']
        try:
            bound.apply_defaults()
            self.param_ids = bound.arguments['ids']
        except AttributeError:
            # can happen if signature is from funcsigs so we have to apply ourselves
            self.param_ids = bound.arguments.get('ids', None)


# -------- tools to get the parametrization mark whatever the pytest version
class _LegacyMark:
    __slots__ = "args", "kwargs"

    def __init__(self, *args, **kwargs):
        """
        Initialize the class.

        Args:
            self: (todo): write your description
        """
        self.args = args
        self.kwargs = kwargs


# ---------------- working on functions
def copy_pytest_marks(from_f, to_f, override=False):
    """Copy all pytest marks from a function or class to another"""
    from_marks = get_pytest_marks_on_function(from_f)
    to_marks = [] if override else get_pytest_marks_on_function(to_f)
    # note: the new marks are appended *after* existing if no override
    to_f.pytestmark = to_marks + from_marks


def get_pytest_marks_on_function(f, as_decorators=False):
    """
    Utility to return *ALL* pytest marks (not only parametrization) applied on a function
    Note that this also works on classes

    :param f:
    :param as_decorators: transforms the marks into decorators before returning them
    :return:
    """
    try:
        mks = f.pytestmark
    except AttributeError:
        try:
            # old pytest < 3: marks are set as fields on the function object
            # but they do not have a particulat type, their type is 'instance'...
            mks = [v for v in vars(f).values() if str(v).startswith("<MarkInfo '")]
        except AttributeError:
            return []

    # in the new version of pytest the marks have to be transformed into decorators explicitly
    if as_decorators:
        return transform_marks_into_decorators(mks, function_marks=True)
    else:
        return mks


def get_pytest_parametrize_marks(f):
    """
    Returns the @pytest.mark.parametrize marks associated with a function (and only those)

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
            if len(mark_info.args) % 2 != 0:
                raise ValueError("internal pytest compatibility error - please report")
            nb_parametrize_decorations = len(mark_info.args) // 2
            if nb_parametrize_decorations > 1 and len(mark_info.kwargs) > 0:
                raise ValueError("Unfortunately with this old pytest version it is not possible to have several "
                                 "parametrization decorators while specifying **kwargs, as all **kwargs are "
                                 "merged, leading to inconsistent results. Either upgrade pytest, remove the **kwargs,"
                                 "or merge all the @parametrize decorators into a single one. **kwargs: %s"
                                 % mark_info.kwargs)
            res = []
            for i in range(nb_parametrize_decorations):
                param_name, param_values = mark_info.args[2*i:2*(i+1)]
                res.append(_ParametrizationMark(_LegacyMark(param_name, param_values, **mark_info.kwargs)))
            return tuple(res)
        else:
            return ()


# ---- tools to reapply marks on test parameter values, whatever the pytest version ----

# Compatibility for the way we put marks on single parameters in the list passed to @pytest.mark.parametrize
# see https://docs.pytest.org/en/3.3.0/skipping.html?highlight=mark%20parametrize#skip-xfail-with-parametrize

# check if pytest.param exists
has_pytest_param = hasattr(pytest, 'param')


if not has_pytest_param:
    # if not this is how it was done
    # see e.g. https://docs.pytest.org/en/2.9.2/skipping.html?highlight=mark%20parameter#skip-xfail-with-parametrize
    def make_marked_parameter_value(argvalues_tuple, marks):
        """
        Make a function that takes a function that takes the value.

        Args:
            argvalues_tuple: (todo): write your description
            marks: (todo): write your description
        """
        if len(marks) > 1:
            raise ValueError("Multiple marks on parameters not supported for old versions of pytest")
        else:
            if not isinstance(argvalues_tuple, tuple):
                raise TypeError("argvalues must be a tuple !")

            # get a decorator for each of the markinfo
            marks_mod = transform_marks_into_decorators(marks, function_marks=False)

            # decorate. Warning: the argvalue MUST be in a tuple
            return marks_mod[0](argvalues_tuple)
else:
    # Otherwise pytest.param exists, it is easier
    def make_marked_parameter_value(argvalues_tuple, marks):
        """
        Make a function that creates a function that takes a value.

        Args:
            argvalues_tuple: (todo): write your description
            marks: (todo): write your description
        """
        if not isinstance(argvalues_tuple, tuple):
            raise TypeError("argvalues must be a tuple !")

        # get a decorator for each of the markinfo
        marks_mod = transform_marks_into_decorators(marks, function_marks=False)

        # decorate
        return pytest.param(*argvalues_tuple, marks=marks_mod)


def transform_marks_into_decorators(marks, function_marks=False):
    """
    Transforms the provided marks (MarkInfo) obtained from marked cases, into MarkDecorator so that they can
    be re-applied to generated pytest parameters in the global @pytest.mark.parametrize.

    :param marks:
    :return:
    """
    marks_mod = []
    try:
        # suppress the warning message that pytest generates when calling pytest.mark.MarkDecorator() directly
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for m in marks:
                md = pytest.mark.MarkDecorator()

                if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
                    if isinstance(m, type(md)):
                        # already a decorator, we can use it
                        marks_mod.append(m)
                    else:
                        md.mark = m
                        marks_mod.append(md)
                else:
                    # always recreate one, type comparison does not work (all generic stuff)
                    md.name = m.name
                    # md.markname = m.name
                    if function_marks:
                        md.args = m.args  # a mark on a function does not include the function in the args
                    else:
                        md.args = m.args[:-1]  # not a function: the value is in the args, remove it
                    md.kwargs = m.kwargs

                    # markinfodecorator = getattr(pytest.mark, markinfo.name)
                    # markinfodecorator(*markinfo.args)

                    marks_mod.append(md)

    except Exception as e:
        warnings.warn("Caught exception while trying to mark case: [%s] %s" % (type(e), e))
    return marks_mod
