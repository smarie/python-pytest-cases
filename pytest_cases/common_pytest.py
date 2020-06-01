from __future__ import division

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature  # noqa

from distutils.version import LooseVersion
from inspect import isgeneratorfunction
from warnings import warn

try:
    from typing import Union, Callable, Any, Optional  # noqa
except ImportError:
    pass

import pytest
from .common_mini_six import string_types


# A decorator that will work to create a fixture containing 'yield', whatever the pytest version, and supports hooks
if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
    def pytest_fixture(hook=None, **kwargs):
        def _decorate(f):
            # call hook if needed
            if hook is not None:
                f = hook(f)

            # create the fixture
            return pytest.fixture(**kwargs)(f)
        return _decorate
else:
    def pytest_fixture(hook=None, name=None, **kwargs):
        """Generator-aware pytest.fixture decorator for legacy pytest versions"""
        def _decorate(f):
            if name is not None:
                # 'name' argument is not supported in this old version, use the __name__ trick.
                f.__name__ = name

            # call hook if needed
            if hook is not None:
                f = hook(f)

            # create the fixture
            if isgeneratorfunction(f):
                return pytest.yield_fixture(**kwargs)(f)
            else:
                return pytest.fixture(**kwargs)(f)
        return _decorate


def remove_duplicates(lst):
    dset = set()
    # relies on the fact that dset.add() always returns None.
    return [item for item in lst
            if item not in dset and not dset.add(item)]


def is_fixture(fixture_fun  # type: Any
               ):
    """
    Returns True if the provided function is a fixture

    :param fixture_fun:
    :return:
    """
    try:
        fixture_fun._pytestfixturefunction  # noqa
        return True
    except AttributeError:
        # not a fixture ?
        return False


def assert_is_fixture(fixture_fun  # type: Any
                      ):
    """
    Raises a ValueError if the provided fixture function is not a fixture.

    :param fixture_fun:
    :return:
    """
    if not is_fixture(fixture_fun):
        raise ValueError("The provided fixture function does not seem to be a fixture: %s. Did you properly decorate "
                         "it ?" % fixture_fun)


def get_fixture_name(fixture_fun  # type: Union[str, Callable]
                     ):
    """
    Internal utility to retrieve the fixture name corresponding to the given fixture function.
    Indeed there is currently no pytest API to do this.

    Note: this function can receive a string, in which case it is directly returned.

    :param fixture_fun:
    :return:
    """
    if isinstance(fixture_fun, string_types):
        return fixture_fun
    assert_is_fixture(fixture_fun)
    try:  # pytest 3
        custom_fixture_name = fixture_fun._pytestfixturefunction.name  # noqa
    except AttributeError:
        try:  # pytest 2
            custom_fixture_name = fixture_fun.func_name  # noqa
        except AttributeError:
            custom_fixture_name = None

    if custom_fixture_name is not None:
        # there is a custom fixture name
        return custom_fixture_name
    else:
        obj__name = getattr(fixture_fun, '__name__', None)
        if obj__name is not None:
            # a function, probably
            return obj__name
        else:
            # a callable object probably
            return str(fixture_fun)


def get_fixture_scope(fixture_fun):
    """
    Internal utility to retrieve the fixture scope corresponding to the given fixture function .
    Indeed there is currently no pytest API to do this.

    :param fixture_fun:
    :return:
    """
    assert_is_fixture(fixture_fun)
    return fixture_fun._pytestfixturefunction.scope  # noqa
    # except AttributeError:
    #     # pytest 2
    #     return fixture_fun.func_scope


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


# ------------ container for the mark information that we grab from the fixtures (`@fixture_plus`)
class _ParametrizationMark:
    """
    Represents the information required by `@fixture_plus` to work.
    """
    __slots__ = "param_names", "param_values", "param_ids"

    def __init__(self, mark):
        bound = get_parametrize_signature().bind(*mark.args, **mark.kwargs)
        try:
            remaining_kwargs = bound.arguments['kwargs']
        except KeyError:
            pass
        else:
            if len(remaining_kwargs) > 0:
                warn("parametrize kwargs not taken into account: %s. Please report it at"
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
        self.args = args
        self.kwargs = kwargs


# ---------------- working on pytest nodes (e.g. Function)

def is_function_node(node):
    try:
        node.function  # noqa
        return True
    except AttributeError:
        return False


def get_parametrization_markers(fnode):
    """
    Returns the parametrization marks on a pytest Function node.
    :param fnode:
    :return:
    """
    if LooseVersion(pytest.__version__) >= LooseVersion('3.4.0'):
        return list(fnode.iter_markers(name="parametrize"))
    else:
        return list(fnode.parametrize)


def get_param_names(fnode):
    """
    Returns a list of parameter names for the given pytest Function node.
    parameterization marks containing several names are split

    :param fnode:
    :return:
    """
    p_markers = get_parametrization_markers(fnode)
    param_names = []
    for paramz_mark in p_markers:
        param_names += get_param_argnames_as_list(paramz_mark.args[0])
    return param_names


# ---------------- working on functions
def get_pytest_marks_on_function(f):
    """
    Utility to return *ALL* pytest marks (not only parametrization) applied on a function

    :param f:
    :return:
    """
    try:
        return f.pytestmark
    except AttributeError:
        try:
            # old pytest < 3: marks are set as fields on the function object
            # but they do not have a particulat type, their type is 'instance'...
            return [v for v in vars(f).values() if str(v).startswith("<MarkInfo '")]
        except AttributeError:
            return []


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


# noinspection PyUnusedLocal
def _pytest_mark_parametrize(argnames, argvalues, ids=None, indirect=False, scope=None, **kwargs):
    """ Fake method to have a reference signature of pytest.mark.parametrize"""
    pass


def get_parametrize_signature():
    """

    :return: a reference signature representing
    """
    return signature(_pytest_mark_parametrize)


# ---------- test ids utils ---------
def combine_ids(paramid_tuples):
    """
    Receives a list of tuples containing ids for each parameterset.
    Returns the final ids, that are obtained by joining the various param ids by '-' for each test node

    :param paramid_tuples:
    :return:
    """
    #
    return ['-'.join(pid for pid in testid) for testid in paramid_tuples]


def make_test_ids(global_ids, id_marks, argnames=None, argvalues=None, precomputed_ids=None):
    """
    Creates the proper id for each test based on (higher precedence first)

     - any specific id mark from a `pytest.param` (`id_marks`)
     - the global `ids` argument of pytest parametrize (`global_ids`)
     - the name and value of parameters (`argnames`, `argvalues`) or the precomputed ids(`precomputed_ids`)

    See also _pytest.python._idvalset method

    :param global_ids:
    :param id_marks:
    :param argnames:
    :param argvalues:
    :param precomputed_ids:
    :return:
    """
    if global_ids is not None:
        # overridden at global pytest.mark.parametrize level - this takes precedence.
        try:  # an explicit list of ids ?
            p_ids = list(global_ids)
        except TypeError:  # a callable to apply on the values
            p_ids = list(global_ids(v) for v in argvalues)
    else:
        # default: values-based
        if precomputed_ids is not None:
            if argnames is not None or argvalues is not None:
                raise ValueError("Only one of `precomputed_ids` or argnames/argvalues should be provided.")
            p_ids = precomputed_ids
        else:
            p_ids = make_test_ids_from_param_values(argnames, argvalues)

    # Finally, local pytest.param takes precedence over everything else
    for i, _id in enumerate(id_marks):
        if _id is not None:
            p_ids[i] = _id
    return p_ids


def make_test_ids_from_param_values(param_names,
                                    param_values,
                                    ):
    """
    Replicates pytest behaviour to generate the ids when there are several parameters in a single `parametrize.
    Note that param_values should not contain marks.

    :param param_names:
    :param param_values:
    :return: a list of param ids
    """
    if isinstance(param_names, string_types):
        raise TypeError("param_names must be an iterable. Found %r" % param_names)

    nb_params = len(param_names)
    if nb_params == 0:
        raise ValueError("empty list provided")
    elif nb_params == 1:
        paramids = []
        for _idx, v in enumerate(param_values):
            _id = mini_idvalset(param_names, (v,), _idx)
            paramids.append(_id)
    else:
        paramids = []
        for _idx, vv in enumerate(param_values):
            if len(vv) != nb_params:
                raise ValueError("Inconsistent lenghts for parameter names and values: '%s' and '%s'"
                                 "" % (param_names, vv))
            _id = mini_idvalset(param_names, vv, _idx)
            paramids.append(_id)
    return paramids


# ---- ParameterSet api ---
def analyze_parameter_set(pmark=None, argnames=None, argvalues=None, ids=None, check_nb=True):
    """
    analyzes a parameter set passed either as a pmark or as distinct
    (argnames, argvalues, ids) to extract/construct the various ids, marks, and
    values

    See also pytest.Metafunc.parametrize method, that calls in particular
    pytest.ParameterSet._for_parametrize and _pytest.python._idvalset

    :param pmark:
    :param argnames:
    :param argvalues:
    :param ids:
    :param check_nb: a bool indicating if we should raise an error if len(argnames) > 1 and any argvalue has
         a different length than len(argnames)
    :return: ids, marks, values
    """
    if pmark is not None:
        if any(a is not None for a in (argnames, argvalues, ids)):
            raise ValueError("Either provide a pmark OR the details")
        argnames = pmark.param_names
        argvalues = pmark.param_values
        ids = pmark.param_ids

    # extract all parameters that have a specific configuration (pytest.param())
    custom_pids, p_marks, p_values = extract_parameterset_info(argnames, argvalues, check_nb=check_nb)

    # get the ids by merging/creating the various possibilities
    p_ids = make_test_ids(argnames=argnames, argvalues=p_values, global_ids=ids, id_marks=custom_pids)

    return p_ids, p_marks, p_values


def extract_parameterset_info(argnames, argvalues, check_nb=True):
    """

    :param argnames: the names in this parameterset
    :param argvalues: the values in this parameterset
    :param check_nb: a bool indicating if we should raise an error if len(argnames) > 1 and any argvalue has
         a different length than len(argnames)
    :return:
    """
    pids = []
    pmarks = []
    pvalues = []
    if isinstance(argnames, string_types):
        raise TypeError("argnames must be an iterable. Found %r" % argnames)
    nbnames = len(argnames)
    for v in argvalues:
        # is this a pytest.param() ?
        if is_marked_parameter_value(v):
            # --id
            _id = get_marked_parameter_id(v)
            pids.append(_id)
            # --marks
            marks = get_marked_parameter_marks(v)
            pmarks.append(marks)  # note: there might be several
            # --value(a tuple if this is a tuple parameter)
            v = get_marked_parameter_values(v)
            if nbnames == 1:
                pvalues.append(v[0])
            else:
                pvalues.append(v)
        else:
            # normal argvalue
            pids.append(None)
            pmarks.append(None)
            pvalues.append(v)

        if check_nb and nbnames > 1 and (len(v) != nbnames):
            raise ValueError("Inconsistent number of values in pytest parametrize: %s items found while the "
                             "number of parameters is %s: %s." % (len(v), nbnames, v))

    return pids, pmarks, pvalues


try:  # pytest 3.x+
    from _pytest.mark import ParameterSet  # noqa

    def is_marked_parameter_value(v):
        return isinstance(v, ParameterSet)

    def get_marked_parameter_marks(v):
        return v.marks

    def get_marked_parameter_values(v):
        return v.values

    def get_marked_parameter_id(v):
        return v.id

except ImportError:  # pytest 2.x
    from _pytest.mark import MarkDecorator

    def is_marked_parameter_value(v):
        return isinstance(v, MarkDecorator)

    def get_marked_parameter_marks(v):
        return [v]

    def get_marked_parameter_values(v):
        return v.args[1:]

    def get_marked_parameter_id(v):
        return v.kwargs.get('id', None)


# ---- tools to reapply marks on test parameter values, whatever the pytest version ----

# Compatibility for the way we put marks on single parameters in the list passed to @pytest.mark.parametrize
# see https://docs.pytest.org/en/3.3.0/skipping.html?highlight=mark%20parametrize#skip-xfail-with-parametrize

try:
    # check if pytest.param exists
    _ = pytest.param
except AttributeError:
    # if not this is how it was done
    # see e.g. https://docs.pytest.org/en/2.9.2/skipping.html?highlight=mark%20parameter#skip-xfail-with-parametrize
    def make_marked_parameter_value(c, marks):
        if len(marks) > 1:
            raise ValueError("Multiple marks on parameters not supported for old versions of pytest")
        else:
            # get a decorator for each of the markinfo
            marks_mod = transform_marks_into_decorators(marks)

            # decorate
            return marks_mod[0](c)
else:
    # Otherwise pytest.param exists, it is easier
    def make_marked_parameter_value(c, marks):
        # get a decorator for each of the markinfo
        marks_mod = transform_marks_into_decorators(marks)

        # decorate
        return pytest.param(c, marks=marks_mod)


def transform_marks_into_decorators(marks):
    """
    Transforms the provided marks (MarkInfo) obtained from marked cases, into MarkDecorator so that they can
    be re-applied to generated pytest parameters in the global @pytest.mark.parametrize.

    :param marks:
    :return:
    """
    marks_mod = []
    try:
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
                md.args = m.args
                md.kwargs = m.kwargs

                # markinfodecorator = getattr(pytest.mark, markinfo.name)
                # markinfodecorator(*markinfo.args)

                marks_mod.append(md)

    except Exception as e:
        warn("Caught exception while trying to mark case: [%s] %s" % (type(e), e))
    return marks_mod


def get_pytest_nodeid(metafunc):
    try:
        return metafunc.definition.nodeid
    except AttributeError:
        return "unknown"


try:
    from _pytest.fixtures import scopes as pt_scopes
except ImportError:
    # pytest 2
    from _pytest.python import scopes as pt_scopes  # noqa


def get_pytest_scopenum(scope_str):
    return pt_scopes.index(scope_str)


def get_pytest_function_scopenum():
    return pt_scopes.index("function")


from _pytest.python import _idval  # noqa


if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
    _idval_kwargs = dict(idfn=None,
                         item=None,  # item is only used by idfn
                         config=None  # if a config hook was available it would be used before this is called)
                         )
else:
    _idval_kwargs = dict(idfn=None,
                         # item=None,  # item is only used by idfn
                         # config=None  # if a config hook was available it would be used before this is called)
                         )


def mini_idval(
        val,      # type: object
        argname,  # type: str
        idx,      # type: int
):
    """
    A simplified version of idval where idfn, item and config do not need to be passed.

    :param val:
    :param argname:
    :param idx:
    :return:
    """
    return _idval(val=val, argname=argname, idx=idx, **_idval_kwargs)


def mini_idvalset(argnames, argvalues, idx):
    """ mimic _pytest.python._idvalset """
    this_id = [
        _idval(val, argname, idx=idx, **_idval_kwargs)
        for val, argname in zip(argvalues, argnames)
    ]
    return "-".join(this_id)
