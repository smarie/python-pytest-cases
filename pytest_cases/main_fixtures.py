# Use true division operator always even in old python 2.x (used in `_get_case_getter_s`)
from __future__ import division

from distutils.version import LooseVersion
from inspect import isgeneratorfunction, getmodule, currentframe
from itertools import product

from decopatch import function_decorator, DECORATED
from makefun import with_signature, add_signature_parameters, remove_signature_parameters

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
    make_marked_parameter_value, extract_parameterset_info
from pytest_cases.main_params import cases_data


def param_fixture(argname, argvalues, ids=None, scope="function"):
    """
    Identical to `param_fixtures` but for a single parameter name.

    :param argname:
    :param argvalues:
    :param ids:
    :param scope: the scope of created fixtures
    :return:
    """
    if "," in argname:
        raise ValueError("`param_fixture` is an alias for `param_fixtures` that can only be used for a single "
                         "parameter name. Use `param_fixtures` instead - but note that it creates several fixtures.")

    # create the fixture
    def _param_fixture(request):
        return request.param
    _param_fixture.__name__ = argname

    return pytest.fixture(scope=scope, params=argvalues, ids=ids)(_param_fixture)


def param_fixtures(argnames, argvalues, ids=None):
    """
    Creates one or several "parameters" fixtures - depending on the number or coma-separated names in `argnames`.

    Note that the (argnames, argvalues, ids) signature is similar to `@pytest.mark.parametrize` for consistency,
    see https://docs.pytest.org/en/latest/reference.html?highlight=pytest.param#pytest-mark-parametrize

    :param argnames:
    :param argvalues:
    :param ids:
    :return:
    """
    created_fixtures = []
    argnames_lst = argnames.replace(' ', '').split(',')

    # create the root fixture that will contain all parameter values
    root_fixture_name = "param_fixtures_root__%s" % ('_'.join(argnames_lst))

    # Add the fixture dynamically: we have to add it to the corresponding module as explained in
    # https://github.com/pytest-dev/pytest/issues/2424
    # grab context from the caller frame
    frame = _get_callerframe()
    module = getmodule(frame)

    # find a non-used fixture name
    if root_fixture_name in dir(module):
        root_fixture_name += '_1'
    i = 1
    while root_fixture_name in dir(module):
        i += 1
        root_fixture_name[-1] += str(i)

    @pytest_fixture_plus(name=root_fixture_name)
    @pytest.mark.parametrize(argnames, argvalues, ids=ids)
    @with_signature("(%s)" % argnames)
    def _root_fixture(**kwargs):
        return tuple(kwargs[k] for k in argnames_lst)

    setattr(module, root_fixture_name, _root_fixture)

    # finally create the sub-fixtures
    for param_idx, argname in enumerate(argnames_lst):
        # create the fixture
        # To fix late binding issue with `param_idx` we add an extra layer of scope
        # See https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
        def _create_fixture(param_idx):
            @pytest_fixture_plus(name=argname)
            @with_signature("(%s)" % root_fixture_name)
            def _param_fixture(**kwargs):
                params = kwargs.pop(root_fixture_name)
                return params[param_idx] if len(argnames_lst) > 1 else params
            return _param_fixture

        created_fixtures.append(_create_fixture(param_idx))

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
        # -- no parametrization: shortcut
        fix_creator = pytest.fixture if not isgeneratorfunction(fixture_func) else yield_fixture
        return fix_creator(scope=scope, autouse=autouse, **kwargs)(fixture_func)

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
    else:
        new_sig = new_sig

    # --common routine used below. Fills kwargs with the appropriate names and values from fixture_params
    def _get_arguments(*args, **kwargs):
        # kwargs contains request
        request = kwargs['request'] if func_needs_request else kwargs.pop('request')

        # populate the parameters
        if len(params_names_or_name_combinations) == 1:
            # remove the simplification
            request.param = [request.param]
        for p_names, fixture_param_value in zip(params_names_or_name_combinations, request.param):
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
        @with_signature(new_sig)
        def wrapped_fixture_func(*args, **kwargs):
            args, kwargs = _get_arguments(*args, **kwargs)
            return fixture_func(*args, **kwargs)

        # transform the created wrapper into a fixture
        fixture_decorator = pytest.fixture(scope=scope, params=final_values, autouse=autouse, ids=final_ids, **kwargs)
        return fixture_decorator(wrapped_fixture_func)

    else:
        # generator function (with a yield statement)
        @with_signature(new_sig)
        def wrapped_fixture_func(*args, **kwargs):
            args, kwargs = _get_arguments(*args, **kwargs)
            for res in fixture_func(*args, **kwargs):
                yield res

        # transform the created wrapper into a fixture
        fixture_decorator = yield_fixture(scope=scope, params=final_values, autouse=autouse, ids=final_ids, **kwargs)
        return fixture_decorator(wrapped_fixture_func)


class UnionFixtureConfig:
    def __init__(self, fixtures):
        self.fixtures = fixtures


def fixture_union(name, *fixtures):
    """
    Creates a fixture that will take all values of the provided fixtures in order.

    :param name:
    :param fixtures:
    :return:
    """
    f_names = [f.func_name if not isinstance(f, str) else f for f in fixtures]

    @with_signature("(%s, request)" % ', '.join(f_names))
    def _new_fixture(request, **kwargs):
        var_to_use = request.param
        return kwargs[var_to_use]

    _new_fixture.__name__ = name
    # TODO scope ?
    return pytest.fixture(params=[UnionFixtureConfig(f_names)])(_new_fixture)


def pytest_parametrize_plus(argnames, argvalues=None, fixtures=None, indirect=False, ids=None, scope=None,
                            **kwargs):
    """
    This is equivalent to `@pytest.mark.parametrize` when `from_fixtures` is not set.

    In addition it offers the possibility to source the list of parameter values from a list of fixtures, in other
    words this creates a "fixture union".

    :param argnames:
    :param argvalues:
    :param fixtures:
    :param indirect:
    :param ids:
    :param scope:
    :param kwargs:
    :return:
    """
    if fixtures is None:
        return pytest.mark.parametrize(argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)
    else:
        if argvalues is not None:
            raise ValueError("If you provide a non-None `from_fixtures` then no `argvalues` should be provided.")

        # TODO
        raise NotImplementedError()
