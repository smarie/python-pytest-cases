from __future__ import division

from distutils.version import LooseVersion
from inspect import isgeneratorfunction
from itertools import product
from warnings import warn

from decopatch import function_decorator, DECORATED
from makefun import with_signature, add_signature_parameters, remove_signature_parameters, wraps

import pytest

try:  # python 3.3+
    from inspect import signature, Parameter
except ImportError:
    from funcsigs import signature, Parameter  # noqa

try:  # type hints, python 3+
    from typing import Callable, Union, Any, List, Iterable, Sequence  # noqa
    from types import ModuleType  # noqa
except ImportError:
    pass

from .common_pytest_lazy_values import get_lazy_args
from .common_pytest import get_pytest_parametrize_marks, make_marked_parameter_value, get_param_argnames_as_list, \
    analyze_parameter_set, combine_ids, is_marked_parameter_value, get_marked_parameter_values, pytest_fixture
from .fixture__creation import get_caller_module, check_name_available, WARN, CHANGE
from .fixture_core1_unions import ignore_unused, is_used_request, NOT_USED, _make_unpack_fixture


def param_fixture(argname,           # type: str
                  argvalues,         # type: Iterable[Any]
                  autouse=False,     # type: bool
                  ids=None,          # type: Union[Callable, List[str]]
                  scope="function",  # type: str
                  hook=None,         # type: Callable[[Callable], Callable]
                  debug=False,       # type: bool
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
    :param debug: print debug messages on stdout to analyze fixture creation (use pytest -s to see them)
    :param kwargs: any other argument for 'fixture'
    :return: the create fixture
    """
    if "," in argname:
        raise ValueError("`param_fixture` is an alias for `param_fixtures` that can only be used for a single "
                         "parameter name. Use `param_fixtures` instead - but note that it creates several fixtures.")
    elif len(argname.replace(' ', '')) == 0:
        raise ValueError("empty argname")

    # todo what if this is called in a class ?
    caller_module = get_caller_module()

    return _create_param_fixture(caller_module, argname, argvalues, autouse=autouse, ids=ids, scope=scope,
                                 hook=hook, debug=debug, **kwargs)


def _create_param_fixture(fixtures_dest,
                          argname,           # type: str
                          argvalues,         # type: Sequence[Any]
                          autouse=False,     # type: bool
                          ids=None,          # type: Union[Callable, List[str]]
                          scope="function",  # type: str
                          hook=None,         # type: Callable[[Callable], Callable]
                          auto_simplify=False,
                          debug=False,
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

        if debug:
            print("Creating unparametrized fixture %r returning %r" % (argname, argvalue_to_return))

        fix = fixture_plus(name=argname, scope=scope, autouse=autouse, ids=ids, hook=hook, **kwargs)(__param_fixture)
    else:
        # create the fixture - set its name so that the optional hook can read it easily
        @with_signature("%s(request)" % argname)
        def __param_fixture(request):
            return request.param

        if debug:
            print("Creating parametrized fixture %r returning %r" % (argname, argvalues))

        fix = fixture_plus(name=argname, scope=scope, autouse=autouse, params=argvalues, ids=ids,
                           hook=hook, **kwargs)(__param_fixture)

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    check_name_available(fixtures_dest, argname, if_name_exists=WARN, caller=param_fixture)
    setattr(fixtures_dest, argname, fix)

    return fix


def param_fixtures(argnames,          # type: str
                   argvalues,         # type: Iterable[Any]
                   autouse=False,     # type: bool
                   ids=None,          # type: Union[Callable, List[str]]
                   scope="function",  # type: str
                   hook=None,         # type: Callable[[Callable], Callable]
                   debug=False,       # type: bool
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
    :param debug: print debug messages on stdout to analyze fixture creation (use pytest -s to see them)
    :param kwargs: any other argument for the created 'fixtures'
    :return: the created fixtures
    """
    argnames_lst = get_param_argnames_as_list(argnames)

    caller_module = get_caller_module()

    if len(argnames_lst) < 2:
        return _create_param_fixture(caller_module, argnames, argvalues, autouse=autouse, ids=ids, scope=scope,
                                     hook=hook, debug=debug, **kwargs)
    else:
        return _create_params_fixture(caller_module, argnames_lst, argvalues, autouse=autouse, ids=ids, scope=scope,
                                      hook=hook, debug=debug, **kwargs)


def _create_params_fixture(fixtures_dest,
                           argnames_lst,      # type: Sequence[str]
                           argvalues,         # type: Sequence[Any]
                           autouse=False,     # type: bool
                           ids=None,          # type: Union[Callable, List[str]]
                           scope="function",  # type: str
                           hook=None,         # type: Callable[[Callable], Callable]
                           debug=False,       # type: bool
                           **kwargs):
    argnames = ','.join(argnames_lst)
    created_fixtures = []

    # create the root fixture that will contain all parameter values
    # note: we sort the list so that the first in alphabetical order appears first. Indeed pytest uses this order.
    root_fixture_name = "%s__param_fixtures_root" % ('_'.join(sorted(argnames_lst)))

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    root_fixture_name = check_name_available(fixtures_dest, root_fixture_name, if_name_exists=CHANGE,
                                             caller=param_fixtures)

    if debug:
        print("Creating parametrized 'root' fixture %r returning %r" % (root_fixture_name, argvalues))

    @fixture_plus(name=root_fixture_name, autouse=autouse, scope=scope, hook=hook, **kwargs)
    @pytest.mark.parametrize(argnames, argvalues, ids=ids)
    @with_signature("%s(%s)" % (root_fixture_name, argnames))
    def _root_fixture(**_kwargs):
        return tuple(_kwargs[k] for k in argnames_lst)

    # Override once again the symbol with the correct contents
    setattr(fixtures_dest, root_fixture_name, _root_fixture)

    # finally create the sub-fixtures
    for param_idx, argname in enumerate(argnames_lst):
        # create the fixture
        # To fix late binding issue with `param_idx` we add an extra layer of scope: a factory function
        # See https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
        def _create_fixture(_param_idx):

            if debug:
                print("Creating nonparametrized 'view' fixture %r returning %r[%s]" % (argname, root_fixture_name, _param_idx))

            @fixture_plus(name=argname, scope=scope, autouse=autouse, hook=hook, **kwargs)
            @with_signature("%s(%s)" % (argname, root_fixture_name))
            def _param_fixture(**_kwargs):
                params = _kwargs.pop(root_fixture_name)
                return params[_param_idx]

            return _param_fixture

        # create it
        fix = _create_fixture(param_idx)

        # add to module
        check_name_available(fixtures_dest, argname, if_name_exists=WARN, caller=param_fixtures)
        setattr(fixtures_dest, argname, fix)

        # collect to return the whole list eventually
        created_fixtures.append(fix)

    return created_fixtures


# Fix for https://github.com/smarie/python-pytest-cases/issues/71
# In order for pytest to allow users to import this symbol in conftest.py
# they should be declared as optional plugin hooks.
# A workaround otherwise would be to remove the 'pytest_' name prefix
# See https://github.com/pytest-dev/pytest/issues/6475
@pytest.hookimpl(optionalhook=True)
def pytest_fixture_plus(*args,
                        **kwargs):
    warn("`pytest_fixture_plus` is deprecated. Please use the new alias `fixture_plus`. "
         "See https://github.com/pytest-dev/pytest/issues/6475", category=DeprecationWarning, stacklevel=2)
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
                 fixture_func=DECORATED,  # noqa
                 **kwargs):
    """ decorator to mark a fixture factory function.

    Identical to `@pytest.fixture` decorator, except that

     - when used in a fixture union (either explicit `fixture_union` or indirect through `@parametrize`+`fixture_ref`
       or `@parametrize_with_cases`), it will not be setup/teardown unnecessarily in tests that do not require it.

     - it supports multi-parametrization with `@pytest.mark.parametrize` as requested in
       https://github.com/pytest-dev/pytest/issues/3960. As a consequence it does not support the `params` and `ids`
       arguments anymore.

     - it supports a new argument `unpack_into` where you can provide names for fixtures where to unpack this fixture
       into.

    As a consequence it does not support the `params` and `ids` arguments anymore.

    :param scope: the scope for which this fixture is shared, one of "function" (default), "class", "module" or
        "session".
    :param autouse: if True, the fixture func is activated for all tests that can see it.  If False (the default) then
        an explicit reference is needed to activate the fixture.
    :param name: the name of the fixture. This defaults to the name of the decorated function. Note: If a fixture is
        used in the same module in which it is defined, the function name of the fixture will be shadowed by the
        function arg that requests the fixture; one way to resolve this is to name the decorated function
        ``fixture_<fixturename>`` and then use ``@pytest.fixture(name='<fixturename>')``.
    :param unpack_into: an optional iterable of names, or string containing coma-separated names, for additional
        fixtures to create to represent parts of this fixture. See `unpack_fixture` for details.
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :param kwargs: other keyword arguments for `@pytest.fixture`
    """
    # todo what if this is called in a class ?

    # the offset is 3 because of @function_decorator (decopatch library)
    return _decorate_fixture_plus(fixture_func, scope=scope, autouse=autouse, name=name, unpack_into=unpack_into,
                                  hook=hook, _caller_module_offset_when_unpack=3, **kwargs)


def _decorate_fixture_plus(fixture_func,
                           scope="function",   # type: str
                           autouse=False,      # type: bool
                           name=None,          # type: str
                           unpack_into=None,   # type: Iterable[str]
                           hook=None,          # type: Callable[[Callable], Callable]
                           _caller_module_offset_when_unpack=3,  # type: int
                           **kwargs):
    """ decorator to mark a fixture factory function.

    Identical to `@pytest.fixture` decorator, except that

     - it supports multi-parametrization with `@pytest.mark.parametrize` as requested in
       https://github.com/pytest-dev/pytest/issues/3960. As a consequence it does not support the `params` and `ids`
       arguments anymore.

     - it supports a new argument `unpack_into` where you can provide names for fixtures where to unpack this fixture
       into.

    :param scope: the scope for which this fixture is shared, one of "function" (default), "class", "module" or
        "session".
    :param autouse: if True, the fixture func is activated for all tests that can see it.  If False (the default) then
        an explicit reference is needed to activate the fixture.
    :param name: the name of the fixture. This defaults to the name of the decorated function. Note: If a fixture is
        used in the same module in which it is defined, the function name of the fixture will be shadowed by the
        function arg that requests the fixture; one way to resolve this is to name the decorated function
        ``fixture_<fixturename>`` and then use ``@pytest.fixture(name='<fixturename>')``.
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
        _make_unpack_fixture(caller_module, unpack_into, name, hook=hook)

    # (1) Collect all @pytest.mark.parametrize markers (including those created by usage of @cases_data)
    parametrizer_marks = get_pytest_parametrize_marks(fixture_func)
    if len(parametrizer_marks) < 1:
        # make the fixture union-aware
        wrapped_fixture_func = ignore_unused(fixture_func)

        # transform the created wrapper into a fixture
        return pytest_fixture(scope=scope, autouse=autouse, hook=hook, **kwargs)(wrapped_fixture_func)

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
                final_values[i] = make_marked_parameter_value((final_values[i],), marks=marks)
    else:
        final_values = list(product(*params_values))
        final_ids = combine_ids(product(*params_ids))
        final_marks = tuple(product(*params_marks))

        # reapply the marks
        for i, marks in enumerate(final_marks):
            ms = [m for mm in marks if mm is not None for m in mm]
            if len(ms) > 0:
                final_values[i] = make_marked_parameter_value((final_values[i],), marks=ms)

    if len(final_values) != len(final_ids):
        raise ValueError("Internal error related to fixture parametrization- please report")

    # (4) wrap the fixture function so as to remove the parameter names and add 'request' if needed
    all_param_names = tuple(v for pnames in params_names_or_name_combinations for v in pnames)

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
    def _map_arguments(*_args, **_kwargs):
        request = _kwargs['request'] if func_needs_request else _kwargs.pop('request')

        # populate the parameters
        if len(params_names_or_name_combinations) == 1:
            _params = [request.param]  # remove the simplification
        else:
            _params = request.param
        for p_names, fixture_param_value in zip(params_names_or_name_combinations, _params):
            if len(p_names) == 1:
                # a single parameter for that generated fixture (@pytest.mark.parametrize with a single name)
                _kwargs[p_names[0]] = get_lazy_args(fixture_param_value)
            else:
                # several parameters for that generated fixture (@pytest.mark.parametrize with several names)
                # unpack all of them and inject them in the kwargs
                for old_p_name, old_p_value in zip(p_names, fixture_param_value):
                    _kwargs[old_p_name] = get_lazy_args(old_p_value)

        return _args, _kwargs

    # --Finally create the fixture function, a wrapper of user-provided fixture with the new signature
    if not isgeneratorfunction(fixture_func):
        # normal function with return statement
        @wraps(fixture_func, new_sig=new_sig)
        def wrapped_fixture_func(*_args, **_kwargs):
            if not is_used_request(_kwargs['request']):
                return NOT_USED
            else:
                _args, _kwargs = _map_arguments(*_args, **_kwargs)
                return fixture_func(*_args, **_kwargs)

    else:
        # generator function (with a yield statement)
        @wraps(fixture_func, new_sig=new_sig)
        def wrapped_fixture_func(*_args, **_kwargs):
            if not is_used_request(_kwargs['request']):
                yield NOT_USED
            else:
                _args, _kwargs = _map_arguments(*_args, **_kwargs)
                for res in fixture_func(*_args, **_kwargs):
                    yield res

    # transform the created wrapper into a fixture
    _make_fix = pytest_fixture(scope=scope, params=final_values, autouse=autouse, hook=hook, ids=final_ids, **kwargs)
    return _make_fix(wrapped_fixture_func)
