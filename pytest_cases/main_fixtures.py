# Use true division operator always even in old python 2.x (used in `_get_case_getter_s`)
from __future__ import division

from distutils.version import LooseVersion
from enum import Enum
from inspect import isgeneratorfunction, getmodule, currentframe
from itertools import product
from warnings import warn

from decopatch import function_decorator, DECORATED
from makefun import with_signature, add_signature_parameters, remove_signature_parameters, wraps

import pytest

try:  # python 3.3+
    from inspect import signature, Parameter
except ImportError:
    from funcsigs import signature, Parameter

try:
    from typing import Type
except ImportError:
    # on old versions of typing module the above does not work. Since our code below has all Type hints quoted it's ok
    pass

try:  # type hints, python 3+
    from typing import Callable, Union, Optional, Any, Tuple, List, Dict, Iterable

    from pytest_cases.case_funcs import CaseData, ExpectedError

    from types import ModuleType

    # Type hint for the simple functions
    CaseFunc = Callable[[], CaseData]

    # Type hint for generator functions
    GeneratedCaseFunc = Callable[[Any], CaseData]
except ImportError:
    pass

from pytest_cases.common import yield_fixture, get_pytest_parametrize_marks, get_test_ids_from_param_values, \
    make_marked_parameter_value, extract_parameterset_info, get_fixture_name
from pytest_cases.main_params import cases_data


def param_fixture(argname, argvalues, autouse=False, ids=None, scope="function", **kwargs):
    """
    Identical to `param_fixtures` but for a single parameter name, so that you can assign its output to a single
    variable.

    :param argname: see fixture `name`
    :param argvalues: see fixture `params`
    :param autouse: see fixture `autouse`
    :param ids: see fixture `ids`
    :param scope: see fixture `scope`
    :param kwargs: any other argument for 'fixture'
    :return:
    """
    if "," in argname:
        raise ValueError("`param_fixture` is an alias for `param_fixtures` that can only be used for a single "
                         "parameter name. Use `param_fixtures` instead - but note that it creates several fixtures.")
    elif len(argname.replace(' ', '')) == 0:
        raise ValueError("empty argname")

    caller_module = get_caller_module()

    return _param_fixture(caller_module, argname, argvalues, autouse=autouse, ids=ids, scope=scope, **kwargs)


def _param_fixture(caller_module, argname, argvalues, autouse=False, ids=None, scope="function", **kwargs):
    """ Internal method shared with param_fixture and param_fixtures """

    # create the fixture
    def __param_fixture(request):
        return request.param

    fix = pytest_fixture_plus(name=argname, scope=scope, autouse=autouse, params=argvalues, ids=ids,
                              **kwargs)(__param_fixture)

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    check_name_available(caller_module, argname, if_name_exists=WARN, caller=param_fixture)
    setattr(caller_module, argname, fix)

    return fix


def get_caller_module(frame_offset=1):
    # grab context from the caller frame
    frame = _get_callerframe(offset=frame_offset)
    return getmodule(frame)


class ExistingFixtureNameError(ValueError):
    """
    Raised by `add_fixture_to_callers_module` when a fixture already exists in a module
    """
    def __init__(self, module, name, caller):
        self.module = module
        self.name = name
        self.caller = caller

    def __str__(self):
        return "Symbol `%s` already exists in module %s and therefore a corresponding fixture can not be created by " \
               "`%s`" % (self.name, self.module, self.caller)


RAISE = 0
WARN = 1
CHANGE = 2


def check_name_available(module,
                         name,                  # type: str
                         if_name_exists=RAISE,  # type: int
                         caller=None,           # type: Callable[[Any], Any]
                         ):
    """
    Routine to

    :param module:
    :param name:
    :param if_name_exists:
    :param caller:
    :return: a name that might be different if policy was CHANGE
    """
    if name in dir(module):
        if caller is None:
            caller = ''

        # Name already exists: act according to policy
        if if_name_exists is RAISE:
            raise ExistingFixtureNameError(module, name, caller)

        elif if_name_exists is WARN:
            warn("%s Overriding symbol %s in module %s" % (caller, name, module))

        elif if_name_exists is CHANGE:
            # find a non-used name in that module
            i = 1
            name2 = name + '_%s' % i
            while name2 in dir(module):
                i += 1
                name2 = name + '_%s' % i
            name = name2
        else:
            raise ValueError("invalid value for `if_name_exists`: %s" % if_name_exists)

    return name


def param_fixtures(argnames, argvalues, autouse=False, ids=None, scope="function", **kwargs):
    """
    Creates one or several "parameters" fixtures - depending on the number or coma-separated names in `argnames`. The
    created fixtures are automatically registered into the callers' module, but you may wish to assign them to
    variables for convenience. In that case make sure that you use the same names, e.g.
    `p, q = param_fixtures('p,q', [(0, 1), (2, 3)])`.

    Note that the (argnames, argvalues, ids) signature is similar to `@pytest.mark.parametrize` for consistency,
    see https://docs.pytest.org/en/latest/reference.html?highlight=pytest.param#pytest-mark-parametrize

    :param argnames: same as `@pytest.mark.parametrize` `argnames`.
    :param argvalues: same as `@pytest.mark.parametrize` `argvalues`.
    :param autouse: see fixture `autouse`
    :param ids: same as `@pytest.mark.parametrize` `ids`
    :param scope: see fixture `scope`
    :param kwargs: any other argument for the created 'fixtures'
    :return:
    """
    created_fixtures = []
    argnames_lst = argnames.replace(' ', '').split(',')

    caller_module = get_caller_module()

    if len(argnames_lst) < 2:
        return _param_fixture(caller_module, argnames, argvalues, autouse=autouse, ids=ids, scope=scope, **kwargs)

    # create the root fixture that will contain all parameter values
    # note: we sort the list so that the first in alphabetical order appears first. Indeed pytest uses this order.
    root_fixture_name = "%s__param_fixtures_root" % ('_'.join(sorted(argnames_lst)))

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    root_fixture_name = check_name_available(caller_module, root_fixture_name, if_name_exists=CHANGE, caller=param_fixtures)

    @pytest_fixture_plus(name=root_fixture_name, autouse=autouse, scope=scope, **kwargs)
    @pytest.mark.parametrize(argnames, argvalues, ids=ids)
    @with_signature("(%s)" % argnames)
    def _root_fixture(**kwargs):
        return tuple(kwargs[k] for k in argnames_lst)

    # Override once again the symbol with the correct contents
    setattr(caller_module, root_fixture_name, _root_fixture)

    # finally create the sub-fixtures
    for param_idx, argname in enumerate(argnames_lst):
        # create the fixture
        # To fix late binding issue with `param_idx` we add an extra layer of scope
        # See https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
        def _create_fixture(param_idx):
            @pytest_fixture_plus(name=argname, scope=scope, autouse=autouse, **kwargs)
            @with_signature("(%s)" % root_fixture_name)
            def _param_fixture(**kwargs):
                params = kwargs.pop(root_fixture_name)
                return params[param_idx]
            return _param_fixture

        # create it
        fix = _create_fixture(param_idx)

        # add to module
        check_name_available(caller_module, argname, if_name_exists=WARN, caller=param_fixtures)
        setattr(caller_module, argname, fix)

        # collect to return the whole list eventually
        created_fixtures.append(fix)

    return created_fixtures


def _get_callerframe(offset=0):
    # inspect.stack is extremely slow, the fastest is sys._getframe or inspect.currentframe().
    # See https://gist.github.com/JettJones/c236494013f22723c1822126df944b12
    # frame = sys._getframe(2 + offset)
    frame = currentframe()
    for _ in range(2 + offset):
        frame = frame.f_back
    return frame


@function_decorator
def cases_fixture(cases=None,                       # type: Union[Callable[[Any], Any], Iterable[Callable[[Any], Any]]]
                  module=None,                      # type: Union[ModuleType, Iterable[ModuleType]]
                  case_data_argname='case_data',    # type: str
                  has_tag=None,                     # type: Any
                  filter=None,                      # type: Callable[[List[Any]], bool]
                  f=DECORATED,
                  **kwargs
                  ):
    """
    DEPRECATED - use double annotation `@pytest_fixture_plus` + `@cases_data` instead

    ```python
    @pytest_fixture_plus
    @cases_data(module=xxx)
    def my_fixture(case_data)
    ```

    Decorates a function so that it becomes a parametrized fixture.

    The fixture will be automatically parametrized with all cases listed in module `module`, or with
    all cases listed explicitly in `cases`.

    Using it with a non-None `module` argument is equivalent to
     * extracting all cases from `module`
     * then decorating your function with @pytest.fixture(params=cases) with all the cases

    So

    ```python
    from pytest_cases import cases_fixture, CaseData

    # import the module containing the test cases
    import test_foo_cases

    @cases_fixture(module=test_foo_cases)
    def foo_fixture(case_data: CaseData):
        ...
    ```

    is equivalent to:

    ```python
    import pytest
    from pytest_cases import get_all_cases, CaseData

    # import the module containing the test cases
    import test_foo_cases

    # manually list the available cases
    cases = get_all_cases(module=test_foo_cases)

    # parametrize the fixture manually
    @pytest.fixture(params=cases)
    def foo_fixture(request):
        case_data = request.param  # type: CaseData
        ...
    ```

    Parameters (cases, module, has_tag, filter) can be used to perform explicit listing, or filtering. See
    `get_all_cases()` for details.

    :param cases: a single case or a hardcoded list of cases to use. Only one of `cases` and `module` should be set.
    :param module: a module or a hardcoded list of modules to use. You may use `THIS_MODULE` to indicate that the
        module is the current one. Only one of `cases` and `module` should be set.
    :param case_data_argname: the optional name of the function parameter that should receive the `CaseDataGetter`
        object. Default is 'case_data'.
    :param has_tag: an optional tag used to filter the cases. Only cases with the given tag will be selected. Only
        cases with the given tag will be selected.
    :param filter: an optional filtering function taking as an input a list of tags associated with a case, and
        returning a boolean indicating if the case should be selected. It will be used to filter the cases in the
        `module`. It both `has_tag` and `filter` are set, both will be applied in sequence.
    :return:
    """
    # apply @cases_data (that will translate to a @pytest.mark.parametrize)
    parametrized_f = cases_data(cases=cases, module=module,
                                case_data_argname=case_data_argname, has_tag=has_tag, filter=filter)(f)
    # apply @pytest_fixture_plus
    return pytest_fixture_plus(**kwargs)(parametrized_f)


@function_decorator
def pytest_fixture_plus(scope="function",
                        autouse=False,
                        name=None,
                        fixture_func=DECORATED,
                        **kwargs):
    """ decorator to mark a fixture factory function.

    Identical to `@pytest.fixture` decorator, except that it supports multi-parametrization with
    `@pytest.mark.parametrize` as requested in https://github.com/pytest-dev/pytest/issues/3960.

    As a consequence it does not support the `params` and `ids` arguments anymore.

    :param scope: the scope for which this fixture is shared, one of
                "function" (default), "class", "module" or "session".
    :param autouse: if True, the fixture func is activated for all tests that
                can see it.  If False (the default) then an explicit
                reference is needed to activate the fixture.
    :param name: the name of the fixture. This defaults to the name of the
                decorated function. Note: If a fixture is used in the same module in
                which it is defined, the function name of the fixture will be
                shadowed by the function arg that requests the fixture; one way
                to resolve this is to name the decorated function
                ``fixture_<fixturename>`` and then use
                ``@pytest.fixture(name='<fixturename>')``.
    :param kwargs: other keyword arguments for `@pytest.fixture`
    """
    # Compatibility for the 'name' argument
    if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
        # pytest version supports "name" keyword argument
        kwargs['name'] = name
    elif name is not None:
        # 'name' argument is not supported in this old version, use the __name__ trick.
        fixture_func.__name__ = name

    # (1) Collect all @pytest.mark.parametrize markers (including those created by usage of @cases_data)
    parametrizer_marks = get_pytest_parametrize_marks(fixture_func)
    if len(parametrizer_marks) < 1:
        return _create_fixture_without_marks(fixture_func, scope, autouse, **kwargs)
    else:
        if 'params' in kwargs:
            raise ValueError(
                "With `pytest_fixture_plus` you cannot mix usage of the keyword argument `params` and of "
                "the pytest.mark.parametrize marks")

    # (2) create the huge "param" containing all params combined
    # --loop (use the same order to get it right)
    params_names_or_name_combinations = []
    params_values = []
    params_ids = []
    params_marks = []
    for pmark in parametrizer_marks:
        # check number of parameter names in this parameterset
        if len(pmark.param_names) < 1:
            raise ValueError("Fixture function '%s' decorated with '@pytest_fixture_plus' has an empty parameter "
                             "name in a @pytest.mark.parametrize mark")

        # remember
        params_names_or_name_combinations.append(pmark.param_names)

        # extract all parameters that have a specific configuration (pytest.param())
        _pids, _pmarks, _pvalues = extract_parameterset_info(pmark.param_names, pmark)

        # Create the proper id for each test
        if pmark.param_ids is not None:
            # overridden at global pytest.mark.parametrize level - this takes precedence.
            try:  # an explicit list of ids ?
                paramids = list(pmark.param_ids)
            except TypeError:  # a callable to apply on the values
                paramids = list(pmark.param_ids(v) for v in _pvalues)
        else:
            # default: values-based...
            paramids = get_test_ids_from_param_values(pmark.param_names, _pvalues)
            # ...but local pytest.param takes precedence
            for i, _id in enumerate(_pids):
                if _id is not None:
                    paramids[i] = _id

        # Finally store the ids, marks, and values for this parameterset
        params_ids.append(paramids)
        params_marks.append(tuple(_pmarks))
        params_values.append(tuple(_pvalues))

    # (3) generate the ids and values, possibly reapplying marks
    if len(params_names_or_name_combinations) == 1:
        # we can simplify - that will be more readable
        final_ids = params_ids[0]
        final_marks = params_marks[0]
        final_values = list(params_values[0])

        # reapply the marks
        for i, marks in enumerate(final_marks):
            if marks is not None:
                final_values[i] = make_marked_parameter_value(final_values[i], marks=marks)
    else:
        final_values = list(product(*params_values))
        final_ids = get_test_ids_from_param_values(params_names_or_name_combinations, product(*params_ids))
        final_marks = tuple(product(*params_marks))

        # reapply the marks
        for i, marks in enumerate(final_marks):
            ms = [m for mm in marks if mm is not None for m in mm]
            if len(ms) > 0:
                final_values[i] = make_marked_parameter_value(final_values[i], marks=ms)

    if len(final_values) != len(final_ids):
        raise ValueError("Internal error related to fixture parametrization- please report")

    # (4) wrap the fixture function so as to remove the parameter names and add 'request' if needed
    all_param_names = tuple(v for l in params_names_or_name_combinations for v in l)

    # --create the new signature that we want to expose to pytest
    old_sig = signature(fixture_func)
    for p in all_param_names:
        if p not in old_sig.parameters:
            raise ValueError("parameter '%s' not found in fixture signature '%s%s'"
                             "" % (p, fixture_func.__name__, old_sig))
    new_sig = remove_signature_parameters(old_sig, *all_param_names)
    # add request if needed
    func_needs_request = 'request' in old_sig.parameters
    if not func_needs_request:
        new_sig = add_signature_parameters(new_sig, first=Parameter('request', kind=Parameter.POSITIONAL_OR_KEYWORD))

    # --common routine used below. Fills kwargs with the appropriate names and values from fixture_params
    def _get_arguments(*args, **kwargs):
        request = kwargs['request'] if func_needs_request else kwargs.pop('request')

        # populate the parameters
        if len(params_names_or_name_combinations) == 1:
            _params = [request.param]  # remove the simplification
        else:
            _params = request.param
        for p_names, fixture_param_value in zip(params_names_or_name_combinations, _params):
            if len(p_names) == 1:
                # a single parameter for that generated fixture (@pytest.mark.parametrize with a single name)
                kwargs[p_names[0]] = fixture_param_value
            else:
                # several parameters for that generated fixture (@pytest.mark.parametrize with several names)
                # unpack all of them and inject them in the kwargs
                for old_p_name, old_p_value in zip(p_names, fixture_param_value):
                    kwargs[old_p_name] = old_p_value

        return args, kwargs

    # --Finally create the fixture function, a wrapper of user-provided fixture with the new signature
    if not isgeneratorfunction(fixture_func):
        # normal function with return statement
        @wraps(fixture_func, new_sig=new_sig)
        def wrapped_fixture_func(*args, **kwargs):
            if not is_used_request(kwargs['request']):
                return NOT_USED
            else:
                args, kwargs = _get_arguments(*args, **kwargs)
                return fixture_func(*args, **kwargs)

        # transform the created wrapper into a fixture
        fixture_decorator = pytest.fixture(scope=scope, params=final_values, autouse=autouse, ids=final_ids, **kwargs)
        return fixture_decorator(wrapped_fixture_func)

    else:
        # generator function (with a yield statement)
        @wraps(fixture_func, new_sig=new_sig)
        def wrapped_fixture_func(*args, **kwargs):
            if not is_used_request(kwargs['request']):
                yield NOT_USED
            else:
                args, kwargs = _get_arguments(*args, **kwargs)
                for res in fixture_func(*args, **kwargs):
                    yield res

        # transform the created wrapper into a fixture
        fixture_decorator = yield_fixture(scope=scope, params=final_values, autouse=autouse, ids=final_ids, **kwargs)
        return fixture_decorator(wrapped_fixture_func)


def _create_fixture_without_marks(fixture_func, scope, autouse, **kwargs):
    """
    creates a fixture for decorated fixture function `fixture_func`.

    :param fixture_func:
    :param scope:
    :param autouse:
    :param kwargs:
    :return:
    """
    # IMPORTANT: even if 'params' is not in kwargs, the fixture
    # can be used in a fixture union and therefore a param will be received
    # on some calls (and the fixture will be called several times - only once for real)
    # - we have to handle the NOT_USED.

    # --create a wrapper where we will be able to auto-detect
    # TODO we could put this in a dedicated wrapper 'ignore_unsused'..

    old_sig = signature(fixture_func)
    # add request if needed
    func_needs_request = 'request' in old_sig.parameters
    if not func_needs_request:
        new_sig = add_signature_parameters(old_sig,
                                           first=Parameter('request', kind=Parameter.POSITIONAL_OR_KEYWORD))
    else:
        new_sig = old_sig
    if not isgeneratorfunction(fixture_func):
        # normal function with return statement
        @wraps(fixture_func, new_sig=new_sig)
        def wrapped_fixture_func(*args, **kwargs):
            request = kwargs['request'] if func_needs_request else kwargs.pop('request')
            if is_used_request(request):
                return fixture_func(*args, **kwargs)
            else:
                return NOT_USED

        # transform the created wrapper into a fixture
        fixture_decorator = pytest.fixture(scope=scope, autouse=autouse, **kwargs)
        return fixture_decorator(wrapped_fixture_func)

    else:
        # generator function (with a yield statement)
        @wraps(fixture_func, new_sig=new_sig)
        def wrapped_fixture_func(*args, **kwargs):
            request = kwargs['request'] if func_needs_request else kwargs.pop('request')
            if is_used_request(request):
                for res in fixture_func(*args, **kwargs):
                    yield res
            else:
                yield NOT_USED

        # transform the created wrapper into a fixture
        fixture_decorator = yield_fixture(scope=scope, autouse=autouse, **kwargs)
        return fixture_decorator(wrapped_fixture_func)


class _NotUsed:
    def __repr__(self):
        return "pytest_cases.NOT_USED"


NOT_USED = _NotUsed()
"""Object representing a fixture value when the fixture is not used"""


class UnionFixtureAlternative(object):
    """A special class that should be used to wrap a fixture name"""

    def __init__(self,
                 fixture_name,
                 idstyle  # type: IdStyle
                 ):
        self.fixture_name = fixture_name
        self.idstyle = idstyle

    # def __str__(self):
    #     that is maybe too dangerous...
    #     return self.fixture_name

    def __repr__(self):
        return "UnionAlternative<%s, idstyle=%s>" % (self.fixture_name, self.idstyle)

    @staticmethod
    def to_list_of_fixture_names(alternatives_lst  # type: List[UnionFixtureAlternative]
                                 ):
        return [f.fixture_name for f in alternatives_lst]


class IdStyle(Enum):
    """
    The enum defining all possible id styles.
    """
    none = None
    explicit = 'explicit'
    compact = 'compact'


def apply_id_style(id, union_fixture_name, idstyle):
    """
    Applies the id style defined in `idstyle` to the given id.
    See https://github.com/smarie/python-pytest-cases/issues/41

    :param id:
    :param union_fixture_name:
    :param idstyle:
    :return:
    """
    if idstyle is IdStyle.none:
        return id
    elif idstyle is IdStyle.explicit:
        return "%s_is_%s" % (union_fixture_name, id)
    elif idstyle is IdStyle.compact:
        return "U%s" % id
    else:
        raise ValueError("Invalid id style")


def is_fixture_union_params(params):
    """
    Internal helper to quickly check if a bunch of parameters correspond to a union fixture.
    :param params:
    :return:
    """
    return len(params) >= 1 and isinstance(params[0], UnionFixtureAlternative)


def is_used_request(request):
    """
    Internal helper to check if a given request for fixture is active or not. Inactive fixtures
    happen when a fixture is not used in the current branch of a UNION fixture.

    This helper is used in all fixtures created in this module.

    :param request:
    :return:
    """
    return getattr(request, 'param', None) is not NOT_USED


def fixture_alternative_to_str(fixture_alternative,  # type: UnionFixtureAlternative
                               ):
    return fixture_alternative.fixture_name


def fixture_union(name, fixtures, scope="function", idstyle='explicit',
                  ids=fixture_alternative_to_str, autouse=False, **kwargs):
    """
    Creates a fixture that will take all values of the provided fixtures in order. That fixture is automatically
    registered into the callers' module, but you may wish to assign it to a variable for convenience. In that case
    make sure that you use the same name, e.g. `a = fixture_union('a', ['b', 'c'])`

    The style of test ids corresponding to the union alternatives can be changed with `idstyle`. Three values are
    allowed:

     - `'explicit'` (default) favors readability,
     - `'compact'` adds a small mark so that at least one sees which parameters are union parameters and which others
       are normal parameters,
     - `None` does not change the ids.

    :param name: the name of the fixture to create
    :param fixtures: an array-like containing fixture names and/or fixture symbols
    :param scope: the scope of the union. Since the union depends on the sub-fixtures, it should be smaller than the
        smallest scope of fixtures referenced.
    :param idstyle: The style of test ids corresponding to the union alternatives. One of `'explicit'` (default),
        `'compact'`, or `None`.
    :param ids: as in pytest. The default value returns the correct fixture
    :param autouse: as in pytest
    :param kwargs: other pytest fixture options. They might not be supported correctly.
    :return: the new fixture. Note: you do not need to capture that output in a symbol, since the fixture is
        automatically registered in your module. However if you decide to do so make sure that you use the same name.
    """
    caller_module = get_caller_module()
    return _fixture_union(caller_module, name, fixtures, scope=scope, idstyle=idstyle, ids=ids, autouse=autouse,
                          **kwargs)


def _fixture_union(caller_module, name, fixtures, idstyle, scope="function", ids=fixture_alternative_to_str,
                   autouse=False, **kwargs):
    """
    Internal implementation for fixture_union

    :param caller_module:
    :param name:
    :param fixtures:
    :param idstyle:
    :param scope:
    :param ids:
    :param autouse:
    :param kwargs:
    :return:
    """
    # test the `fixtures` argument to avoid common mistakes
    if not isinstance(fixtures, (tuple, set, list)):
        raise TypeError("fixture_union: the `fixtures` argument should be a tuple, set or list")

    # validate the idstyle
    idstyle = IdStyle(idstyle)

    # first get all required fixture names
    f_names = []
    for f in fixtures:
        # possibly get the fixture name if the fixture symbol was provided
        f_names.append(get_fixture_name(f) if not isinstance(f, str) else f)

    if len(f_names) < 1:
        raise ValueError("Empty fixture unions are not permitted")

    # then generate the body of our union fixture. It will require all of its dependent fixtures and receive as
    # a parameter the name of the fixture to use
    @with_signature("(%s, request)" % ', '.join(f_names))
    def _new_fixture(request, **all_fixtures):
        if not is_used_request(request):
            return NOT_USED
        else:
            alternative = request.param
            if isinstance(alternative, UnionFixtureAlternative):
                fixture_to_use = alternative.fixture_name
                return all_fixtures[fixture_to_use]
            else:
                raise TypeError("Union Fixture %s received invalid parameter type: %s. Please report this issue."
                                "" % (name, alternative.__class__))

    _new_fixture.__name__ = name

    # finally create the fixture per se.
    # WARNING we do not use pytest.fixture but pytest_fixture_plus so that NOT_USED is discarded
    f_decorator = pytest_fixture_plus(scope=scope,
                                      params=[UnionFixtureAlternative(_name, idstyle) for _name in f_names],
                                      autouse=autouse, ids=ids, **kwargs)
    fix = f_decorator(_new_fixture)

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    check_name_available(caller_module, name, if_name_exists=WARN, caller=param_fixture)
    setattr(caller_module, name, fix)

    return fix


class fixture_ref:
    """
    A reference to a fixture, to be used in `pytest_parametrize_plus`.
    You can create it from a fixture name or a fixture object (function).
    """
    __slots__ = 'fixture',

    def __init__(self, fixture):
        self.fixture = fixture


def pytest_parametrize_plus(argnames, argvalues, indirect=False, ids=None, scope=None, **kwargs):
    """
    Equivalent to `@pytest.mark.parametrize` but also supports the fact that in argvalues one can include references to
    fixtures with `fixture_ref(<fixture>)` where <fixture> can be the fixture name or fixture function.

    When such a fixture reference is detected in the argvalues, a new function-scope fixture will be created with a
    unique name, and the test function will be wrapped so as to be injected with the correct parameters. Special test
    ids will be created to illustrate the switching between normal parameters and fixtures.

    :param argnames:
    :param argvalues:
    :param indirect:
    :param ids:
    :param scope:
    :param kwargs:
    :return:
    """
    # make sure that we do not destroy the argvalues if it is provided as an iterator
    argvalues = list(argvalues)

    # find if there are fixture references in the values provided
    fixture_indices = []
    for i, v in enumerate(argvalues):
        if isinstance(v, fixture_ref):
            fixture_indices.append(i)

    if len(fixture_indices) == 0:
        # no fixture reference: do as usual
        return pytest.mark.parametrize(argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)
    else:
        # there are fixture references: we have to create a specific decorator
        caller_module = get_caller_module()
        all_param_names = argnames.replace(' ', '').split(',')

        def create_param_fixture(from_i, to_i, p_fix_name):
            """ Routine that will be used to create a parameter fixture for argvalues between prev_i and i"""
            selected_argvalues = argvalues[from_i:to_i]
            try:
                # an explicit list of ids
                selected_ids = ids[from_i:to_i]
            except TypeError:
                # a callable to create the ids
                selected_ids = ids

            if to_i == from_i + 1:
                p_fix_name = "%s_is_%s" % (p_fix_name, from_i)
            else:
                p_fix_name = "%s_is_%sto%s" % (p_fix_name, from_i, to_i - 1)
            p_fix_name = check_name_available(caller_module, p_fix_name, if_name_exists=CHANGE, caller=pytest_parametrize_plus)
            param_fix = _param_fixture(caller_module, p_fix_name, selected_argvalues, selected_ids)
            return param_fix

        # then create the decorator
        def parametrize_plus_decorate(test_func):
            """
            A decorator that wraps the test function so that instead of receiving the parameter names, it receives the
            new fixture. All other decorations are unchanged.

            :param test_func:
            :return:
            """
            # first check if the test function has the parameters as arguments
            old_sig = signature(test_func)
            for p in all_param_names:
                if p not in old_sig.parameters:
                    raise ValueError("parameter '%s' not found in test function signature '%s%s'"
                                     "" % (p, test_func.__name__, old_sig))

            # The base name for all fixtures that will be created below
            # style_template = "%s_param__%s"
            style_template = "%s_%s"
            base_name = style_template % (test_func.__name__, argnames.replace(' ', '').replace(',', '_'))
            base_name = check_name_available(caller_module, base_name, if_name_exists=CHANGE, caller=pytest_parametrize_plus)

            # Retrieve (if ref) or create (for normal argvalues) the fixtures that we will union
            # TODO important note: we could either wish to create one fixture for parameter value or to create one for
            #  each consecutive group as shown below. This should not lead to different results but perf might differ.
            #  maybe add a parameter in the signature so that users can test it ?
            fixtures_to_union = []
            fixtures_to_union_names_for_ids = []
            prev_i = -1
            for i in fixture_indices:
                if i > prev_i + 1:
                    param_fix = create_param_fixture(prev_i + 1, i, base_name)
                    fixtures_to_union.append(param_fix)
                    fixtures_to_union_names_for_ids.append(get_fixture_name(param_fix))

                fixtures_to_union.append(argvalues[i].fixture)
                id_for_fixture = apply_id_style(get_fixture_name(argvalues[i].fixture), base_name, IdStyle.explicit)
                fixtures_to_union_names_for_ids.append(id_for_fixture)
                prev_i = i

            # last bit if any
            i = len(argvalues)
            if i > prev_i + 1:
                param_fix = create_param_fixture(prev_i + 1, i, base_name)
                fixtures_to_union.append(param_fix)
                fixtures_to_union_names_for_ids.append(get_fixture_name(param_fix))

            # Finally create a "main" fixture with a unique name for this test function
            # note: the function automatically registers it in the module
            # note 2: idstyle is set to None because we provide an explicit enough list of ids
            big_param_fixture = _fixture_union(caller_module, base_name, fixtures_to_union, idstyle=None,
                                               ids=fixtures_to_union_names_for_ids)

            # --create the new test function's signature that we want to expose to pytest
            # it is the same than existing, except that we want to replace all parameters with the new fixture

            new_sig = remove_signature_parameters(old_sig, *all_param_names)
            new_sig = add_signature_parameters(new_sig, Parameter(base_name, kind=Parameter.POSITIONAL_OR_KEYWORD))

            # --Finally create the fixture function, a wrapper of user-provided fixture with the new signature
            def replace_paramfixture_with_values(kwargs):
                # remove the created fixture value
                encompassing_fixture = kwargs.pop(base_name)
                # and add instead the parameter values
                if len(all_param_names) > 1:
                    for i, p in enumerate(all_param_names):
                        kwargs[p] = encompassing_fixture[i]
                else:
                    kwargs[all_param_names[0]] = encompassing_fixture
                # return
                return kwargs

            if not isgeneratorfunction(test_func):
                # normal test function with return statement
                @wraps(test_func, new_sig=new_sig)
                def wrapped_test_func(*args, **kwargs):
                    if kwargs.get(base_name, None) is NOT_USED:
                        return NOT_USED
                    else:
                        replace_paramfixture_with_values(kwargs)
                        return test_func(*args, **kwargs)

            else:
                # generator test function (with one or several yield statement)
                @wraps(test_func, new_sig=new_sig)
                def wrapped_test_func(*args, **kwargs):
                    if kwargs.get(base_name, None) is NOT_USED:
                        yield NOT_USED
                    else:
                        replace_paramfixture_with_values(kwargs)
                        for res in test_func(*args, **kwargs):
                            yield res

            # move all pytest marks from the test function to the wrapper
            # not needed because the __dict__ is automatically copied when we use @wraps
            #   move_all_pytest_marks(test_func, wrapped_test_func)

            # With this hack we will be ordered correctly by pytest https://github.com/pytest-dev/pytest/issues/4429
            wrapped_test_func.place_as = test_func

            # return the new test function
            return wrapped_test_func

        return parametrize_plus_decorate
