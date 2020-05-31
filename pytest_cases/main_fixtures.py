# Use true division operator always even in old python 2.x (used in `_get_case_getter_s`)
from __future__ import division

from distutils.version import LooseVersion
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

from pytest_cases.common import yield_fixture, get_pytest_parametrize_marks, make_marked_parameter_value, \
    get_fixture_name, get_param_argnames_as_list, analyze_parameter_set, combine_ids, get_fixture_scope, \
    remove_duplicates, extract_parameterset_info, is_marked_parameter_value, get_marked_parameter_values, mini_idvalset
from pytest_cases.main_params import cases_data
from pytest_cases.mini_six import string_types


def unpack_fixture(argnames,
                   fixture,
                   hook=None  # type: Callable[[Callable], Callable]
                   ):
    """
    Creates several fixtures with names `argnames` from the source `fixture`. Created fixtures will correspond to
    elements unpacked from `fixture` in order. For example if `fixture` is a tuple of length 2, `argnames="a,b"` will
    create two fixtures containing the first and second element respectively.

    The created fixtures are automatically registered into the callers' module, but you may wish to assign them to
    variables for convenience. In that case make sure that you use the same names,
    e.g. `a, b = unpack_fixture('a,b', 'c')`.

    ```python
    import pytest
    from pytest_cases import unpack_fixture, fixture_plus

    @fixture_plus
    @pytest.mark.parametrize("o", ['hello', 'world'])
    def c(o):
        return o, o[0]

    a, b = unpack_fixture("a,b", c)

    def test_function(a, b):
        assert a[0] == b
    ```

    :param argnames: same as `@pytest.mark.parametrize` `argnames`.
    :param fixture: a fixture name string or a fixture symbol. If a fixture symbol is provided, the created fixtures
        will have the same scope. If a name is provided, they will have scope='function'. Note that in practice the
        performance loss resulting from using `function` rather than a higher scope is negligible since the created
        fixtures' body is a one-liner.
    :return: the created fixtures.
    """
    # get caller module to create the symbols
    caller_module = get_caller_module()
    return _unpack_fixture(caller_module, argnames, fixture, hook=hook)


def _unpack_fixture(caller_module, argnames, fixture, hook):
    """

    :param caller_module:
    :param argnames:
    :param fixture:
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :return:
    """
    # unpack fixture names to create if needed
    argnames_lst = get_param_argnames_as_list(argnames)

    # possibly get the source fixture name if the fixture symbol was provided
    source_f_name = get_fixture_name(fixture)
    if not isinstance(fixture, string_types):
        scope = get_fixture_scope(fixture)
    else:
        # we dont have a clue about the real scope, so lets use function scope
        scope = 'function'

    # finally create the sub-fixtures
    created_fixtures = []
    for value_idx, argname in enumerate(argnames_lst):
        # create the fixture
        # To fix late binding issue with `value_idx` we add an extra layer of scope: a factory function
        # See https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
        def _create_fixture(value_idx):
            # no need to autouse=True: this fixture does not bring any added value in terms of setup.
            @fixture_plus(name=argname, scope=scope, autouse=False, hook=hook)
            @with_signature("%s(%s)" % (argname, source_f_name))
            def _param_fixture(**kwargs):
                source_fixture_value = kwargs.pop(source_f_name)
                # unpack
                return source_fixture_value[value_idx]

            return _param_fixture

        # create it
        fix = _create_fixture(value_idx)

        # add to module
        check_name_available(caller_module, argname, if_name_exists=WARN, caller=unpack_fixture)
        setattr(caller_module, argname, fix)

        # collect to return the whole list eventually
        created_fixtures.append(fix)

    return created_fixtures


def param_fixture(argname,
                  argvalues,
                  autouse=False,     # type: bool
                  ids=None,          # type: Union[Callable, List[str]]
                  scope="function",  # type: str
                  hook=None,         # type: Callable[[Callable], Callable]
                  **kwargs):
    """
    Identical to `param_fixtures` but for a single parameter name, so that you can assign its output to a single
    variable.

    ```python
    import pytest
    from pytest_cases import param_fixtures, param_fixture

    # create a single parameter fixture
    my_parameter = param_fixture("my_parameter", [1, 2, 3, 4])

    @pytest.fixture
    def fixture_uses_param(my_parameter):
        ...

    def test_uses_param(my_parameter, fixture_uses_param):
        ...
    ```

    :param argname: see fixture `name`
    :param argvalues: see fixture `params`
    :param autouse: see fixture `autouse`
    :param ids: see fixture `ids`
    :param scope: see fixture `scope`
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :param kwargs: any other argument for 'fixture'
    :return: the create fixture
    """
    if "," in argname:
        raise ValueError("`param_fixture` is an alias for `param_fixtures` that can only be used for a single "
                         "parameter name. Use `param_fixtures` instead - but note that it creates several fixtures.")
    elif len(argname.replace(' ', '')) == 0:
        raise ValueError("empty argname")

    caller_module = get_caller_module()

    return _create_param_fixture(caller_module, argname, argvalues, autouse=autouse, ids=ids, scope=scope,
                                 hook=hook, **kwargs)


def _create_param_fixture(caller_module,
                          argname,
                          argvalues,
                          autouse=False,     # type: bool
                          ids=None,          # type: Union[Callable, List[str]]
                          scope="function",  # type: str
                          hook=None,         # type: Callable[[Callable], Callable]
                          auto_simplify=False,
                          **kwargs):
    """ Internal method shared with param_fixture and param_fixtures """

    if auto_simplify and len(argvalues) == 1:
        # Simplification: do not parametrize the fixture, it will directly return the single value
        argvalue_to_return = argvalues[0]
        if is_marked_parameter_value(argvalue_to_return):
            argvalue_to_return = get_marked_parameter_values(argvalue_to_return)

        # create the fixture - set its name so that the optional hook can read it easily
        @with_signature("%s()" % argname)
        def __param_fixture():
            return argvalue_to_return

        fix = fixture_plus(name=argname, scope=scope, autouse=autouse, ids=ids, hook=hook, **kwargs)(__param_fixture)
    else:
        # create the fixture - set its name so that the optional hook can read it easily
        @with_signature("%s(request)" % argname)
        def __param_fixture(request):
            return request.param

        fix = fixture_plus(name=argname, scope=scope, autouse=autouse, params=argvalues, ids=ids,
                           hook=hook, **kwargs)(__param_fixture)

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


def param_fixtures(argnames,
                   argvalues,
                   autouse=False,     # type: bool
                   ids=None,          # type: Union[Callable, List[str]]
                   scope="function",  # type: str
                   hook=None,         # type: Callable[[Callable], Callable]
                   **kwargs):
    """
    Creates one or several "parameters" fixtures - depending on the number or coma-separated names in `argnames`. The
    created fixtures are automatically registered into the callers' module, but you may wish to assign them to
    variables for convenience. In that case make sure that you use the same names, e.g.
    `p, q = param_fixtures('p,q', [(0, 1), (2, 3)])`.

    Note that the (argnames, argvalues, ids) signature is similar to `@pytest.mark.parametrize` for consistency,
    see https://docs.pytest.org/en/latest/reference.html?highlight=pytest.param#pytest-mark-parametrize

    ```python
    import pytest
    from pytest_cases import param_fixtures, param_fixture

    # create a 2-tuple parameter fixture
    arg1, arg2 = param_fixtures("arg1, arg2", [(1, 2), (3, 4)])

    @pytest.fixture
    def fixture_uses_param2(arg2):
        ...

    def test_uses_param2(arg1, arg2, fixture_uses_param2):
        ...
    ```

    :param argnames: same as `@pytest.mark.parametrize` `argnames`.
    :param argvalues: same as `@pytest.mark.parametrize` `argvalues`.
    :param autouse: see fixture `autouse`
    :param ids: same as `@pytest.mark.parametrize` `ids`
    :param scope: see fixture `scope`
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :param kwargs: any other argument for the created 'fixtures'
    :return: the created fixtures
    """
    created_fixtures = []
    argnames_lst = get_param_argnames_as_list(argnames)

    caller_module = get_caller_module()

    if len(argnames_lst) < 2:
        return _create_param_fixture(caller_module, argnames, argvalues, autouse=autouse, ids=ids, scope=scope,
                                     hook=hook, **kwargs)

    # create the root fixture that will contain all parameter values
    # note: we sort the list so that the first in alphabetical order appears first. Indeed pytest uses this order.
    root_fixture_name = "%s__param_fixtures_root" % ('_'.join(sorted(argnames_lst)))

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    root_fixture_name = check_name_available(caller_module, root_fixture_name, if_name_exists=CHANGE,
                                             caller=param_fixtures)

    @fixture_plus(name=root_fixture_name, autouse=autouse, scope=scope, hook=hook, **kwargs)
    @pytest.mark.parametrize(argnames, argvalues, ids=ids)
    @with_signature("%s(%s)" % (root_fixture_name, argnames))
    def _root_fixture(**kwargs):
        return tuple(kwargs[k] for k in argnames_lst)

    # Override once again the symbol with the correct contents
    setattr(caller_module, root_fixture_name, _root_fixture)

    # finally create the sub-fixtures
    for param_idx, argname in enumerate(argnames_lst):
        # create the fixture
        # To fix late binding issue with `param_idx` we add an extra layer of scope: a factory function
        # See https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
        def _create_fixture(param_idx):
            @fixture_plus(name=argname, scope=scope, autouse=autouse, hook=hook, **kwargs)
            @with_signature("%s(%s)" % (argname, root_fixture_name))
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
    DEPRECATED - use double annotation `@fixture_plus` + `@cases_data` instead

    ```python
    @fixture_plus
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
    # apply @fixture_plus
    return fixture_plus(**kwargs)(parametrized_f)


# Fix for https://github.com/smarie/python-pytest-cases/issues/71
# In order for pytest to allow users to import this symbol in conftest.py
# they should be declared as optional plugin hooks.
# A workaround otherwise would be to remove the 'pytest_' name prefix
# See https://github.com/pytest-dev/pytest/issues/6475
@pytest.hookimpl(optionalhook=True)
def pytest_fixture_plus(*args,
                        **kwargs):
    warn("`pytest_fixture_plus` is deprecated. Please use the new alias `fixture_plus`. "
         "See https://github.com/pytest-dev/pytest/issues/6475")
    if len(args) == 1:
        if callable(args[0]):
            return _decorate_fixture_plus(args[0], _caller_module_offset_when_unpack=2, **kwargs)
    def _fixture_plus(f):
        return _decorate_fixture_plus(f, *args, _caller_module_offset_when_unpack=2, **kwargs)
    return _fixture_plus


@function_decorator
def fixture_plus(scope="function",  # type: str
                 autouse=False,     # type: bool
                 name=None,         # type: str
                 unpack_into=None,  # type: Iterable[str]
                 hook=None,         # type: Callable[[Callable], Callable]
                 fixture_func=DECORATED,
                 **kwargs):
    """ decorator to mark a fixture factory function.

    Identical to `@pytest.fixture` decorator, except that

     - it supports multi-parametrization with `@pytest.mark.parametrize` as requested in
       https://github.com/pytest-dev/pytest/issues/3960. As a consequence it does not support the `params` and `ids`
       arguments anymore.

     - it supports a new argument `unpack_into` where you can provide names for fixtures where to unpack this fixture
       into.

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
    :param unpack_into: an optional iterable of names, or string containing coma-separated names, for additional
        fixtures to create to represent parts of this fixture. See `unpack_fixture` for details.
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :param kwargs: other keyword arguments for `@pytest.fixture`
    """
    # the offset is 3 because of @function_decorator (decopatch library)
    return _decorate_fixture_plus(fixture_func, scope=scope, autouse=autouse, name=name, unpack_into=unpack_into,
                                  hook=hook, _caller_module_offset_when_unpack=3, **kwargs)


def _decorate_fixture_plus(fixture_func,
                           scope="function",
                           autouse=False,
                           name=None,
                           unpack_into=None,
                           hook=None,          # type: Callable[[Callable], Callable]
                           _caller_module_offset_when_unpack=3,
                           **kwargs):
    """ decorator to mark a fixture factory function.

    Identical to `@pytest.fixture` decorator, except that

     - it supports multi-parametrization with `@pytest.mark.parametrize` as requested in
       https://github.com/pytest-dev/pytest/issues/3960. As a consequence it does not support the `params` and `ids`
       arguments anymore.

     - it supports a new argument `unpack_into` where you can provide names for fixtures where to unpack this fixture
       into.

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
    :param unpack_into: an optional iterable of names, or string containing coma-separated names, for additional
        fixtures to create to represent parts of this fixture. See `unpack_fixture` for details.
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :param kwargs: other keyword arguments for `@pytest.fixture`
    """
    if name is not None:
        # Compatibility for the 'name' argument
        if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):
            # pytest version supports "name" keyword argument
            kwargs['name'] = name
        elif name is not None:
            # 'name' argument is not supported in this old version, use the __name__ trick.
            fixture_func.__name__ = name

    # if unpacking is requested, do it first
    if unpack_into is not None:
        # get the future fixture name if needed
        if name is None:
            name = fixture_func.__name__

        # get caller module to create the symbols
        caller_module = get_caller_module(frame_offset=_caller_module_offset_when_unpack)
        _unpack_fixture(caller_module, unpack_into, name, hook=hook)

    # (1) Collect all @pytest.mark.parametrize markers (including those created by usage of @cases_data)
    parametrizer_marks = get_pytest_parametrize_marks(fixture_func)
    if len(parametrizer_marks) < 1:
        return _create_fixture_without_marks(fixture_func, scope, autouse, hook=hook, **kwargs)
    else:
        if 'params' in kwargs:
            raise ValueError(
                "With `fixture_plus` you cannot mix usage of the keyword argument `params` and of "
                "the pytest.mark.parametrize marks")

    # (2) create the huge "param" containing all params combined
    # --loop (use the same order to get it right)
    params_names_or_name_combinations = []
    params_values = []
    params_ids = []
    params_marks = []
    for pmark in parametrizer_marks:
        # -- pmark is a single @pytest.parametrize mark. --

        # check number of parameter names in this parameterset
        if len(pmark.param_names) < 1:
            raise ValueError("Fixture function '%s' decorated with '@fixture_plus' has an empty parameter "
                             "name in a @pytest.mark.parametrize mark")

        # remember the argnames
        params_names_or_name_combinations.append(pmark.param_names)

        # analyse contents, extract marks and custom ids, apply custom ids
        _paramids, _pmarks, _pvalues = analyze_parameter_set(pmark=pmark, check_nb=True)

        # Finally store the ids, marks, and values for this parameterset
        params_ids.append(_paramids)
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
        final_ids = combine_ids(product(*params_ids))
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

        # call hook if needed
        if hook is not None:
            wrapped_fixture_func = hook(wrapped_fixture_func)

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

        # call hook if needed
        if hook is not None:
            wrapped_fixture_func = hook(wrapped_fixture_func)

        # transform the created wrapper into a fixture
        fixture_decorator = yield_fixture(scope=scope, params=final_values, autouse=autouse, ids=final_ids, **kwargs)
        return fixture_decorator(wrapped_fixture_func)


def _create_fixture_without_marks(fixture_func, scope, autouse, hook, **kwargs):
    """
    creates a fixture for decorated fixture function `fixture_func`.

    :param fixture_func:
    :param scope:
    :param autouse:
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
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

        # call hook if needed
        if hook is not None:
            wrapped_fixture_func = hook(wrapped_fixture_func)

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

        # call hook if needed
        if hook is not None:
            wrapped_fixture_func = hook(wrapped_fixture_func)

        # transform the created wrapper into a fixture
        fixture_decorator = yield_fixture(scope=scope, autouse=autouse, **kwargs)
        return fixture_decorator(wrapped_fixture_func)


class _NotUsed:
    def __repr__(self):
        return "pytest_cases.NOT_USED"


NOT_USED = _NotUsed()
"""Object representing a fixture value when the fixture is not used"""


class UnionIdMakers(object):
    """
    The enum defining all possible id styles for union fixture parameters ("alternatives")
    """
    @classmethod
    def nostyle(cls, param):
        return param.alternative_name

    @classmethod
    def explicit(cls, param):
        return "%s_is_%s" % (param.union_name, param.alternative_name)

    @classmethod
    def compact(cls, param):
        return "U%s" % param.alternative_name

    @classmethod
    def get(cls, style  # type: str
            ):
        # type: (...) -> Callable[[Any], str]
        """
        Returns a function that one can use as the `ids` argument in parametrize, applying the given id style.
        See https://github.com/smarie/python-pytest-cases/issues/41

        :param idstyle:
        :return:
        """
        style = style or 'nostyle'
        try:
            return getattr(cls, style)
        except AttributeError:
            raise ValueError("Unknown style: %r" % style)


class UnionFixtureAlternative(object):
    """Defines an "alternative", used to parametrize a fixture union"""
    __slots__ = 'union_name', 'alternative_name'

    def __init__(self,
                 union_name,
                 alternative_name,
                 ):
        self.union_name = union_name
        self.alternative_name = alternative_name

    # def __str__(self):
    #     # although this would be great to have a default id directly, it may be
    #     # very confusion for debugging so I prefer that we use id_maker('none')
    #     # to make this default behaviour explicit and not pollute the debugging process
    #     return self.alternative_name

    def __repr__(self):
        return "%s<%s=%s>" % (self.__class__.__name__, self.union_name, self.alternative_name)

    @staticmethod
    def to_list_of_fixture_names(alternatives_lst  # type: List[UnionFixtureAlternative]
                                 ):
        res = []
        for f in alternatives_lst:
            if is_marked_parameter_value(f):
                f = get_marked_parameter_values(f)[0]
            res.append(f.alternative_name)
        return res


class InvalidParamsList(Exception):
    """
    Exception raised when users attempt to provide a non-iterable `argvalues` in pytest parametrize.
    See https://docs.pytest.org/en/latest/reference.html#pytest-mark-parametrize-ref
    """
    __slots__ = 'params',

    def __init__(self, params):
        self.params = params

    def __str__(self):
        return "Invalid parameters list (`argvalues`) in pytest parametrize: %s" % self.params


def is_fixture_union_params(params):
    """
    Internal helper to quickly check if a bunch of parameters correspond to a union fixture.
    :param params:
    :return:
    """
    try:
        if len(params) < 1:
            return False
        else:
            p0 = params[0]
            if is_marked_parameter_value(p0):
                p0 = get_marked_parameter_values(p0)[0]
            return isinstance(p0, UnionFixtureAlternative)
    except TypeError:
        raise InvalidParamsList(params)


def is_used_request(request):
    """
    Internal helper to check if a given request for fixture is active or not. Inactive fixtures
    happen when a fixture is not used in the current branch of a UNION fixture.

    This helper is used in all fixtures created in this module.

    :param request:
    :return:
    """
    return getattr(request, 'param', None) is not NOT_USED


def fixture_union(name,                # type: str
                  fixtures,            # type: Iterable[Union[str, Callable]]
                  scope="function",    # type: str
                  idstyle='explicit',  # type: Optional[str]
                  ids=None,            # type: Union[Callable, List[str]]
                  unpack_into=None,    # type: Iterable[str]
                  autouse=False,       # type: bool
                  hook=None,           # type: Callable[[Callable], Callable]
                  **kwargs):
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
    :param unpack_into: an optional iterable of names, or string containing coma-separated names, for additional
        fixtures to create to represent parts of this fixture. See `unpack_fixture` for details.
    :param autouse: as in pytest
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :param kwargs: other pytest fixture options. They might not be supported correctly.
    :return: the new fixture. Note: you do not need to capture that output in a symbol, since the fixture is
        automatically registered in your module. However if you decide to do so make sure that you use the same name.
    """
    caller_module = get_caller_module()

    # test the `fixtures` argument to avoid common mistakes
    if not isinstance(fixtures, (tuple, set, list)):
        raise TypeError("fixture_union: the `fixtures` argument should be a tuple, set or list")

    # unpack the pytest.param marks
    custom_pids, p_marks, fixtures = extract_parameterset_info((name, ), fixtures)

    # get all required fixture names
    f_names = []
    for f in fixtures:
        # possibly get the fixture name if the fixture symbol was provided
        f_names.append(get_fixture_name(f))

    # create all alternatives and reapply the marks on them
    fix_alternatives = []
    f_names_args = []
    for _name, _id, _mark in zip(f_names, custom_pids, p_marks):
        # create the alternative object
        alternative = UnionFixtureAlternative(union_name=name, alternative_name=_name)

        # remove duplicates in the fixture arguments: each is required only once by the union fixture to create
        if _name in f_names_args:
            warn("Creating a fixture union %r where two alternatives are the same fixture %r." % (name, _name))
        else:
            f_names_args.append(_name)

        # reapply the marks
        if _id is not None or (_mark or ()) != ():
            alternative = pytest.param(alternative, id=_id, marks=_mark or ())
        fix_alternatives.append(alternative)

    return _fixture_union(caller_module, name,
                          fix_alternatives=fix_alternatives, unique_fix_alt_names=f_names_args,
                          scope=scope, idstyle=idstyle, ids=ids, autouse=autouse,
                          hook=hook, unpack_into=unpack_into, **kwargs)


def _fixture_union(caller_module,
                   name,                  # type: str
                   fix_alternatives,      # type: Iterable[UnionFixtureAlternative]
                   unique_fix_alt_names,  # type: List[str]
                   scope="function",      # type: str
                   idstyle="explicit",    # type: str
                   ids=None,              # type: Union[Callable, List[str]]
                   unpack_into=None,      # type: Iterable[str]
                   autouse=False,         # type: bool
                   hook=None,             # type: Callable[[Callable], Callable]
                   **kwargs):
    """
    Internal implementation for fixture_union

    :param caller_module:
    :param name:
    :param fix_alternatives:
    :param unique_fix_alt_names:
    :param idstyle:
    :param scope:
    :param ids:
    :param unpack_into:
    :param autouse:
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :param kwargs:
    :return:
    """
    # get the ids generator corresponding to the idstyle
    if ids is None:
        ids = UnionIdMakers.get(idstyle)

    if len(fix_alternatives) < 1:
        raise ValueError("Empty fixture unions are not permitted")

    # then generate the body of our union fixture. It will require all of its dependent fixtures and receive as
    # a parameter the name of the fixture to use
    @with_signature("%s(%s, request)" % (name, ', '.join(unique_fix_alt_names)))
    def _new_fixture(request, **all_fixtures):
        if not is_used_request(request):
            return NOT_USED
        else:
            _alternative = request.param
            if isinstance(_alternative, UnionFixtureAlternative):
                fixture_to_use = _alternative.alternative_name
                return all_fixtures[fixture_to_use]
            else:
                raise TypeError("Union Fixture %s received invalid parameter type: %s. Please report this issue."
                                "" % (name, _alternative.__class__))

    # finally create the fixture per se.
    # WARNING we do not use pytest.fixture but fixture_plus so that NOT_USED is discarded
    f_decorator = fixture_plus(scope=scope,
                               params=fix_alternatives,
                               autouse=autouse, ids=ids, hook=hook, **kwargs)
    fix = f_decorator(_new_fixture)

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    check_name_available(caller_module, name, if_name_exists=WARN, caller=param_fixture)
    setattr(caller_module, name, fix)

    # if unpacking is requested, do it here
    if unpack_into is not None:
        _unpack_fixture(caller_module, argnames=unpack_into, fixture=name, hook=hook)

    return fix


def _fixture_product(caller_module,
                     name,                # type: str
                     fixtures_or_values,
                     fixture_positions,
                     scope="function",    # type: str
                     ids=None,            # type: Union[Callable, List[str]]
                     unpack_into=None,    # type: Iterable[str]
                     autouse=False,       # type: bool
                     hook=None,           # type: Callable[[Callable], Callable]
                     **kwargs):
    """
    Internal implementation for fixture products created by pytest parametrize plus.

    :param caller_module:
    :param name:
    :param fixtures_or_values:
    :param fixture_positions:
    :param idstyle:
    :param scope:
    :param ids:
    :param unpack_into:
    :param autouse:
    :param kwargs:
    :return:
    """
    # test the `fixtures` argument to avoid common mistakes
    if not isinstance(fixtures_or_values, (tuple, set, list)):
        raise TypeError("fixture_product: the `fixtures_or_values` argument should be a tuple, set or list")

    _tuple_size = len(fixtures_or_values)

    # first get all required fixture names
    f_names = [None] * _tuple_size
    for f_pos in fixture_positions:
        # possibly get the fixture name if the fixture symbol was provided
        f = fixtures_or_values[f_pos]
        if isinstance(f, fixture_ref):
            f = f.fixture
        # and remember the position in the tuple
        f_names[f_pos] = get_fixture_name(f)

    # remove duplicates by making it an ordered set
    all_names = remove_duplicates((n for n in f_names if n is not None))
    if len(all_names) < 1:
        raise ValueError("Empty fixture products are not permitted")

    def _tuple_generator(all_fixtures):
        for i in range(_tuple_size):
            fix_at_pos_i = f_names[i]
            if fix_at_pos_i is None:
                # fixed value
                yield fixtures_or_values[i]
            else:
                # fixture value
                yield all_fixtures[fix_at_pos_i]

    # then generate the body of our product fixture. It will require all of its dependent fixtures
    @with_signature("(%s)" % ', '.join(all_names))
    def _new_fixture(**all_fixtures):
        return tuple(_tuple_generator(all_fixtures))

    _new_fixture.__name__ = name

    # finally create the fixture per se.
    # WARNING we do not use pytest.fixture but fixture_plus so that NOT_USED is discarded
    f_decorator = fixture_plus(scope=scope, autouse=autouse, ids=ids, hook=hook, **kwargs)
    fix = f_decorator(_new_fixture)

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    check_name_available(caller_module, name, if_name_exists=WARN, caller=param_fixture)
    setattr(caller_module, name, fix)

    # if unpacking is requested, do it here
    if unpack_into is not None:
        _unpack_fixture(caller_module, argnames=unpack_into, fixture=name, hook=hook)

    return fix


class fixture_ref:
    """
    A reference to a fixture, to be used in `parametrize_plus`.
    You can create it from a fixture name or a fixture object (function).
    """
    __slots__ = 'fixture',

    def __init__(self, fixture):
        self.fixture = fixture


# Fix for https://github.com/smarie/python-pytest-cases/issues/71
# In order for pytest to allow users to import this symbol in conftest.py
# they should be declared as optional plugin hooks.
# A workaround otherwise would be to remove the 'pytest_' name prefix
# See https://github.com/pytest-dev/pytest/issues/6475
@pytest.hookimpl(optionalhook=True)
def pytest_parametrize_plus(*args,
                            **kwargs):
    warn("`pytest_parametrize_plus` is deprecated. Please use the new alias `parametrize_plus`. "
         "See https://github.com/pytest-dev/pytest/issues/6475")
    return _parametrize_plus(*args, **kwargs)


class ParamAlternative(UnionFixtureAlternative):
    """Defines an "alternative", used to parametrize a fixture union in the context of parametrize_plus"""
    __slots__ = ('argnames', )

    def __init__(self,
                 union_name,
                 alternative_name,
                 argnames,
                 ):
        super(ParamAlternative, self).__init__(union_name=union_name, alternative_name=alternative_name)
        self.argnames = argnames

    @property
    def argnames_str(self):
        return '_'.join(self.argnames)


class SingleParamAlternative(ParamAlternative):
    """alternative class for single parameter value"""
    __slots__ = 'argvalues_index', 'argvalues'

    def __init__(self,
                 union_name,
                 alternative_name,
                 argnames,
                 argvalues_index,
                 argvalues
                 ):
        super(SingleParamAlternative, self).__init__(union_name=union_name, alternative_name=alternative_name,
                                                     argnames=argnames)
        self.argvalues_index = argvalues_index
        self.argvalues = argvalues

    def get_id(self):
        # return "-".join(self.argvalues)
        return mini_idvalset(self.argnames, self.argvalues, idx=self.argvalues_index)


class MultiParamAlternative(ParamAlternative):
    """alternative class for multiple parameter values"""
    __slots__ = 'argvalues_index_from', 'argvalues_index_to'

    def __init__(self,
                 union_name,
                 alternative_name,
                 argnames,
                 argvalues_index_from,
                 argvalues_index_to
                 ):
        super(MultiParamAlternative, self).__init__(union_name=union_name, alternative_name=alternative_name,
                                                    argnames=argnames)
        self.argvalues_index_from = argvalues_index_from
        self.argvalues_index_to = argvalues_index_to


class FixtureParamAlternative(ParamAlternative):
    """alternative class for a single parameter containing a fixture ref"""
    __slots__ = 'argvalues_index',

    def __init__(self,
                 union_name,
                 alternative_name,
                 argnames,
                 argvalues_index,
                 ):
        super(FixtureParamAlternative, self).__init__(union_name=union_name, alternative_name=alternative_name,
                                                      argnames=argnames)
        self.argvalues_index = argvalues_index


class ProductParamAlternative(ParamAlternative):
    """alternative class for a single product parameter containing fixture refs"""
    __slots__ = 'argvalues_index'

    def __init__(self,
                 union_name,
                 alternative_name,
                 argnames,
                 argvalues_index,
                 ):
        super(ProductParamAlternative, self).__init__(union_name=union_name, alternative_name=alternative_name,
                                                      argnames=argnames)
        self.argvalues_index = argvalues_index


class ParamIdMakers(object):
    """ 'Enum' of id styles for param ids """

    # @staticmethod
    # def nostyle(param):
    #     return param.alternative_name

    @staticmethod
    def explicit(param  # type: ParamAlternative
                 ):
        if isinstance(param, SingleParamAlternative):
            # return "%s_is_P%s" % (param.param_name, param.argvalues_index)
            return "%s_is_%s" % (param.argnames_str, param.get_id())
        elif isinstance(param, MultiParamAlternative):
            return "%s_is_P%stoP%s" % (param.argnames_str, param.argvalues_index_from, param.argvalues_index_to - 1)
        elif isinstance(param, FixtureParamAlternative):
            return "%s_is_%s" % (param.argnames_str, param.alternative_name)
        elif isinstance(param, ProductParamAlternative):
            return "%s_is_P%s" % (param.argnames_str, param.argvalues_index)
        else:
            raise TypeError("Unsupported alternative: %r" % param)

    # @staticmethod
    # def compact(param):
    #     return "U%s" % param.alternative_name

    @classmethod
    def get(cls, style  # type: str
            ):
        # type: (...) -> Callable[[Any], str]
        """
        Returns a function that one can use as the `ids` argument in parametrize, applying the given id style.
        See https://github.com/smarie/python-pytest-cases/issues/41

        :param idstyle:
        :return:
        """
        style = style or 'nostyle'
        try:
            return getattr(cls, style)
        except AttributeError:
            raise ValueError("Unknown style: %r" % style)


def parametrize_plus(argnames,
                     argvalues,
                     indirect=False,      # type: bool
                     ids=None,            # type: Union[Callable, List[str]]
                     idstyle='explicit',  # type: str
                     scope=None,          # type: str
                     hook=None,           # type: Callable[[Callable], Callable]
                     **kwargs):
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
    :param idstyle:
    :param scope:
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :param kwargs:
    :return:
    """
    return _parametrize_plus(argnames, argvalues, indirect=indirect, ids=ids, idstyle=idstyle, scope=scope, hook=hook,
                             **kwargs)


def _parametrize_plus(argnames,
                      argvalues,
                      indirect=False,      # type: bool
                      ids=None,            # type: Union[Callable, List[str]]
                      idstyle='explicit',  # type: str
                      scope=None,          # type: str
                      hook=None,           # type: Callable[[Callable], Callable]
                      _frame_offset=2,
                      **kwargs):
    # make sure that we do not destroy the argvalues if it is provided as an iterator
    try:
        argvalues = list(argvalues)
    except TypeError:
        raise InvalidParamsList(argvalues)

    # get the param names
    initial_argnames = argnames
    argnames = get_param_argnames_as_list(argnames)
    nb_params = len(argnames)

    # extract all marks and custom ids.
    # Do not check consistency of sizes argname/argvalue as a fixture_ref can stand for several argvalues.
    marked_argvalues = argvalues
    custom_pids, p_marks, argvalues = extract_parameterset_info(argnames, argvalues, check_nb=False)

    # find if there are fixture references in the values provided
    fixture_indices = []
    if nb_params == 1:
        for i, v in enumerate(argvalues):
            if isinstance(v, fixture_ref):
                fixture_indices.append((i, None))
    elif nb_params > 1:
        for i, v in enumerate(argvalues):
            if isinstance(v, fixture_ref):
                # a fixture ref is used for several parameters at the same time
                fixture_indices.append((i, None))
            elif len(v) == 1 and isinstance(v[0], fixture_ref):
                # same than above but it was in a pytest.mark
                # a fixture ref is used for several parameters at the same time
                fixture_indices.append((i, None))
                # unpack it
                argvalues[i] = v[0]
            else:
                # check for consistency
                if len(v) != len(argnames):
                    raise ValueError("Inconsistent number of values in pytest parametrize: %s items found while the "
                                     "number of parameters is %s: %s." % (len(v), len(argnames), v))

                # let's dig into the tuple
                fix_pos_list = [j for j, _pval in enumerate(v) if isinstance(_pval, fixture_ref)]
                if len(fix_pos_list) > 0:
                    # there is at least one fixture ref inside the tuple
                    fixture_indices.append((i, fix_pos_list))
    del i

    if len(fixture_indices) == 0:
        # no fixture reference: shortcut, do as usual (note that the hook wont be called since no fixture is created)
        return pytest.mark.parametrize(initial_argnames, marked_argvalues, indirect=indirect,
                                       ids=ids, scope=scope, **kwargs)
    else:
        # there are fixture references: we have to create a specific decorator
        caller_module = get_caller_module(frame_offset=_frame_offset)
        param_names_str = '_'.join(argnames).replace(' ', '')

        def _make_idfun_for_params(argnames, nb_positions):
            """
            Creates an id creating function that will use 'argnames' as the argnames
            instead of the one(s) received by pytest. We use this in the case of param fixture
            creation because on one side we need a unique fixture name so it is big and horrible,
            but on the other side we want the id to rather reflect the simple argnames, no that fixture name.

            :param argnames:
            :param nb_positions:
            :return:
            """
            # create a new make id function with its own local counter of parameter
            def _tmp_make_id(argvalues):
                _tmp_make_id._i += 1
                if _tmp_make_id._i >= nb_positions:
                    raise ValueError("Internal error, please report")
                argvalues = argvalues if len(argnames) > 1 else (argvalues,)
                return mini_idvalset(argnames, argvalues, idx=_tmp_make_id._i)

            # init its positions counter
            _tmp_make_id._i = -1
            return _tmp_make_id

        def _create_params_alt(test_func_name, union_name, from_i, to_i, hook):
            """ Routine that will be used to create a parameter fixture for argvalues between prev_i and i"""

            single_param = (to_i == from_i + 1)

            if single_param:
                i = from_i

                # Create a unique fixture name
                p_fix_name = "%s_%s_P%s" % (test_func_name, param_names_str, i)
                p_fix_name = check_name_available(caller_module, p_fix_name, if_name_exists=CHANGE,
                                                  caller=parametrize_plus)
                # Create the fixture that will return the unique parameter value ("auto-simplify" flag)
                # IMPORTANT that fixture is NOT parametrized so has no id nor marks: use argvalues not marked_argvalues
                _create_param_fixture(caller_module, argname=p_fix_name, argvalues=argvalues[i:i+1], hook=hook,
                                      auto_simplify=True)

                # Create the alternative
                argvals = (argvalues[i],) if nb_params == 1 else argvalues[i]
                p_fix_alt = SingleParamAlternative(union_name=union_name, alternative_name=p_fix_name,
                                                   argnames=argnames, argvalues_index=i, argvalues=argvals)
                # Finally copy the custom id/marks on the ParamAlternative if any
                if is_marked_parameter_value(marked_argvalues[i]):
                    p_fix_alt = pytest.param(p_fix_alt, id=marked_argvalues[i].id, marks=marked_argvalues[i].marks)

            else:
                # Create a unique fixture name
                p_fix_name = "%s_%s_is_P%stoP%s" % (test_func_name, param_names_str, from_i, to_i - 1)
                p_fix_name = check_name_available(caller_module, p_fix_name, if_name_exists=CHANGE,
                                                  caller=parametrize_plus)

                # If an explicit list of ids was provided, slice it. Otherwise use the provided callable
                try:
                    p_ids = ids[from_i:to_i]
                except TypeError:
                    # callable ? otherwise default to a customized id maker that replaces the fixture name
                    # that we use (p_fix_name) with a simpler name in the ids (just the argnames)
                    p_ids = ids or _make_idfun_for_params(argnames=argnames, nb_positions=(to_i - from_i))

                # Create the fixture that will take all these parameter values
                # That fixture WILL be parametrized, this is why we propagate the p_ids and use the marked values
                _create_param_fixture(caller_module, argname=p_fix_name, argvalues=marked_argvalues[from_i:to_i],
                                      ids=p_ids, hook=hook)

                # Create the corresponding alternative
                p_fix_alt = MultiParamAlternative(union_name=union_name, alternative_name=p_fix_name, argnames=argnames,
                                                  argvalues_index_from=from_i, argvalues_index_to=to_i)
                # no need to copy the custom id/marks to the ParamAlternative: they were passed above already

            return p_fix_name, p_fix_alt

        def _create_fixture_ref_alt(union_name, i):
            # Get the referenced fixture name
            f_fix_name = get_fixture_name(argvalues[i].fixture)

            # Create the alternative
            f_fix_alt = FixtureParamAlternative(union_name=union_name, alternative_name=f_fix_name,
                                                argnames=argnames, argvalues_index=i)
            # Finally copy the custom id/marks on the ParamAlternative if any
            if is_marked_parameter_value(marked_argvalues[i]):
                f_fix_alt = pytest.param(f_fix_alt, id=marked_argvalues[i].id, marks=marked_argvalues[i].marks)

            return f_fix_name, f_fix_alt

        def _create_fixture_ref_product(union_name, i, fixture_ref_positions, test_func_name, hook):

            # If an explicit list of ids was provided, slice it. Otherwise use the provided callable
            try:
                p_ids = ids[i]
            except TypeError:
                p_ids = ids  # callable

            # values to use:
            p_values = argvalues[i]

            # Create a unique fixture name
            p_fix_name = "%s_%s_P%s" % (test_func_name, param_names_str, i)
            p_fix_name = check_name_available(caller_module, p_fix_name, if_name_exists=CHANGE,
                                              caller=parametrize_plus)

            # Create the fixture
            new_product_fix = _fixture_product(caller_module, name=p_fix_name, fixtures_or_values=p_values,
                                               fixture_positions=fixture_ref_positions, hook=hook, ids=p_ids)

            # Create the corresponding alternative
            p_fix_alt = ProductParamAlternative(union_name=union_name, alternative_name=p_fix_name,
                                                argnames=argnames, argvalues_index=i)
            # copy the custom id/marks to the ParamAlternative if any
            if is_marked_parameter_value(marked_argvalues[i]):
                p_fix_alt = pytest.param(p_fix_alt, id=marked_argvalues[i].id, marks=marked_argvalues[i].marks)

            return p_fix_name, p_fix_alt

        # then create the decorator
        def parametrize_plus_decorate(test_func):
            """
            A decorator that wraps the test function so that instead of receiving the parameter names, it receives the
            new fixture. All other decorations are unchanged.

            :param test_func:
            :return:
            """
            test_func_name = test_func.__name__

            # first check if the test function has the parameters as arguments
            old_sig = signature(test_func)
            for p in argnames:
                if p not in old_sig.parameters:
                    raise ValueError("parameter '%s' not found in test function signature '%s%s'"
                                     "" % (p, test_func_name, old_sig))

            # The name for the final "union" fixture
            # style_template = "%s_param__%s"
            main_fixture_style_template = "%s_%s"
            fixture_union_name = main_fixture_style_template % (test_func_name, param_names_str)
            fixture_union_name = check_name_available(caller_module, fixture_union_name, if_name_exists=CHANGE,
                                                      caller=parametrize_plus)

            # Retrieve (if ref) or create (for normal argvalues) the fixtures that we will union
            fixture_alternatives = []
            prev_i = -1
            for i, j_list in fixture_indices:
                # A/ Is there any non-empty group of 'normal' parameters before the fixture_ref at <i> ? If so, handle.
                if i > prev_i + 1:
                    # create a new "param" fixture parametrized with all of that consecutive group.
                    # TODO important note: we could either wish to create one fixture for parameter value or to create
                    #  one for each consecutive group as shown below. This should not lead to different results but perf
                    #  might differ. Maybe add a parameter in the signature so that users can test it ?
                    #  this would make the ids more readable by removing the "P2toP3"-like ids
                    p_fix_name, p_fix_alt = _create_params_alt(test_func_name=test_func_name, hook=hook,
                                                               union_name=fixture_union_name, from_i=prev_i + 1, to_i=i)
                    fixture_alternatives.append((p_fix_name, p_fix_alt))

                # B/ Now handle the fixture ref at position <i>
                if j_list is None:
                    # argvalues[i] contains a single argvalue that is a fixture_ref : add the referenced fixture
                    f_fix_name, f_fix_alt = _create_fixture_ref_alt(union_name=fixture_union_name, i=i)
                    fixture_alternatives.append((f_fix_name, f_fix_alt))

                else:
                    # argvalues[i] is a tuple, some of them being fixture_ref. create a fixture refering to all of them
                    prod_fix_name, prod_fix_alt = _create_fixture_ref_product(union_name=fixture_union_name, i=i,
                                                                              fixture_ref_positions=j_list,
                                                                              test_func_name=test_func_name, hook=hook)
                    fixture_alternatives.append((prod_fix_name, prod_fix_alt))

                prev_i = i

            # C/ handle last consecutive group of normal parameters, if any
            i = len(argvalues)
            if i > prev_i + 1:
                p_fix_name, p_fix_alt = _create_params_alt(test_func_name=test_func_name, union_name=fixture_union_name,
                                                           from_i=prev_i + 1, to_i=i, hook=hook)
                fixture_alternatives.append((p_fix_name, p_fix_alt))

            # TO DO if fixtures_to_union has length 1, simplify ? >> No, we leave such "optimization" to the end user

            # consolidate the list of alternatives
            fix_alternatives = tuple(a[1] for a in fixture_alternatives)

            # and the list of their names. Duplicates should be removed here
            fix_alt_names = []
            for a, alt in fixture_alternatives:
                if a not in fix_alt_names:
                    fix_alt_names.append(a)
                else:
                    # this should only happen when the alternative is directly a fixture reference
                    assert isinstance(alt, FixtureParamAlternative), \
                        "Created fixture names are not unique, please report"

            # Finally create a "main" fixture with a unique name for this test function
            # TODO if `ids` were provided, we have to "cut the part where the product params appear

            # note: the function automatically registers it in the module
            big_param_fixture = _fixture_union(caller_module, name=fixture_union_name,
                                               fix_alternatives=fix_alternatives, unique_fix_alt_names=fix_alt_names,
                                               ids=ids or ParamIdMakers.get(idstyle), hook=hook)

            # --create the new test function's signature that we want to expose to pytest
            # it is the same than existing, except that we want to replace all parameters with the new fixture
            # first check where we should insert the new parameters (where is the first param we remove)
            for _first_idx, _n in enumerate(old_sig.parameters):
                if _n in argnames:
                    break
            # then remove all parameters that will be replaced by the new fixture
            new_sig = remove_signature_parameters(old_sig, *argnames)
            # finally insert the new fixture in that position. Indeed we can not insert first or last, because
            # 'self' arg (case of test class methods) should stay first and exec order should be preserved when possible
            new_sig = add_signature_parameters(new_sig, custom_idx=_first_idx,
                                               custom=Parameter(fixture_union_name,
                                                                kind=Parameter.POSITIONAL_OR_KEYWORD))

            # --Finally create the fixture function, a wrapper of user-provided fixture with the new signature
            def replace_paramfixture_with_values(kwargs):
                # remove the created fixture value
                encompassing_fixture = kwargs.pop(fixture_union_name)
                # and add instead the parameter values
                if nb_params > 1:
                    for i, p in enumerate(argnames):
                        kwargs[p] = encompassing_fixture[i]
                else:
                    kwargs[argnames[0]] = encompassing_fixture
                # return
                return kwargs

            if not isgeneratorfunction(test_func):
                # normal test function with return statement
                @wraps(test_func, new_sig=new_sig)
                def wrapped_test_func(*args, **kwargs):
                    if kwargs.get(fixture_union_name, None) is NOT_USED:
                        return NOT_USED
                    else:
                        replace_paramfixture_with_values(kwargs)
                        return test_func(*args, **kwargs)

            else:
                # generator test function (with one or several yield statements)
                @wraps(test_func, new_sig=new_sig)
                def wrapped_test_func(*args, **kwargs):
                    if kwargs.get(fixture_union_name, None) is NOT_USED:
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
