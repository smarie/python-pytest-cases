# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from __future__ import division

from inspect import isgeneratorfunction
from warnings import warn

from makefun import with_signature, add_signature_parameters, wraps

import pytest

try:  # python 3.3+
    from inspect import signature, Parameter
except ImportError:
    from funcsigs import signature, Parameter  # noqa

try:  # type hints, python 3+
    from typing import Callable, Union, Optional, Any, List, Iterable, Sequence  # noqa
    from types import ModuleType  # noqa
except ImportError:
    pass

from .common_mini_six import string_types
from .common_pytest import get_fixture_name, is_marked_parameter_value, get_marked_parameter_values, pytest_fixture, \
    extract_parameterset_info, get_param_argnames_as_list, get_fixture_scope
from .fixture__creation import get_caller_module, check_name_available, WARN


class _NotUsed:
    def __repr__(self):
        """
        Return a repr representation of a repr__.

        Args:
            self: (todo): write your description
        """
        return "pytest_cases.NOT_USED"


NOT_USED = _NotUsed()
"""Object representing a fixture value when the fixture is not used"""


class UnionIdMakers(object):
    """
    The enum defining all possible id styles for union fixture parameters ("alternatives")
    """
    @classmethod
    def nostyle(cls, param):
        """
        Return the nostyle parameter.

        Args:
            cls: (todo): write your description
            param: (todo): write your description
        """
        return param.alternative_name

    @classmethod
    def explicit(cls, param):
        """
        Returns an encoded function name for the given a parameter.

        Args:
            cls: (todo): write your description
            param: (todo): write your description
        """
        return "%s_is_%s" % (param.union_name, param.alternative_name)

    @classmethod
    def compact(cls, param):
        """
        Compact the function parameter for the parameter.

        Args:
            cls: (todo): write your description
            param: (todo): write your description
        """
        return "U%s" % param.alternative_name

    @classmethod
    def get(cls, style  # type: str
            ):
        # type: (...) -> Callable[[Any], str]
        """
        Returns a function that one can use as the `ids` argument in parametrize, applying the given id style.
        See https://github.com/smarie/python-pytest-cases/issues/41

        :param style:
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
        """
        Initialize a new union.

        Args:
            self: (todo): write your description
            union_name: (str): write your description
            alternative_name: (str): write your description
        """
        self.union_name = union_name
        self.alternative_name = alternative_name

    # def __str__(self):
    #     # although this would be great to have a default id directly, it may be
    #     # very confusion for debugging so I prefer that we use id_maker('none')
    #     # to make this default behaviour explicit and not pollute the debugging process
    #     return self.alternative_name

    def __repr__(self):
        """
        Return a human - readable representation of this object.

        Args:
            self: (todo): write your description
        """
        return "%s<%s=%s>" % (self.__class__.__name__, self.union_name, self.alternative_name)

    @staticmethod
    def to_list_of_fixture_names(alternatives_lst  # type: List[UnionFixtureAlternative]
                                 ):
        """
        Converts a list of alternative list to a list.

        Args:
            alternatives_lst: (todo): write your description
        """
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
        """
        Initialize the parameters

        Args:
            self: (todo): write your description
            params: (dict): write your description
        """
        self.params = params

    def __str__(self):
        """
        Return a string representation of this object.

        Args:
            self: (todo): write your description
        """
        return "Invalid parameters list (`argvalues`) in pytest parametrize: %s" % self.params


def is_fixture_union_params(params):
    """
    Internal helper to quickly check if a bunch of parameters correspond to a union fixture.

    Note: unfortunately `pytest` transform all params to a list when a @pytest.fixture is created,
    so we can not pass a subclass of list to do the trick, we really have to work on the list elements.
    :param params:
    :return:
    """
    try:
        if len(params) < 1:
            return False
        else:
            if getattr(params, '__module__', '').startswith('pytest_cases'):
                # a value_ref_tuple or another proxy object created somewhere in our code, not a list
                return False
            p0 = params[0]
            if is_marked_parameter_value(p0):
                p0 = get_marked_parameter_values(p0)[0]
            return isinstance(p0, UnionFixtureAlternative)
    except:  # noqa
        # be conservative
        # an iterable or the like - we do not use such things when we cope with fixture_refs and unions
        return False


def is_used_request(request):
    """
    Internal helper to check if a given request for fixture is active or not.
    Inactive fixtures happen when a fixture is not used in the current branch of a UNION fixture.

    All fixtures that need to be union-compliant have to be decorated with `@ignore_unused`

    :param request:
    :return:
    """
    return getattr(request, 'param', None) is not NOT_USED


def ignore_unused(fixture_func):
    """
    A decorator for fixture functions so that they are compliant with fixture unions.
    It

     - adds the `request` fixture dependency to their signature if needed
     - filters the calls based on presence of the `NOT_USED` token in the request params.

    IMPORTANT: even if 'params' is not in kwargs, the fixture can be used in a fixture union and therefore a param
    *will* be received on some calls (and the fixture will be called several times - only once for real) - we have to
    handle the NOT_USED.

    :param fixture_func:
    :return:
    """
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
            """
            Decorator for the wrapped request if the request.

            Args:
            """
            request = kwargs['request'] if func_needs_request else kwargs.pop('request')
            if is_used_request(request):
                return fixture_func(*args, **kwargs)
            else:
                return NOT_USED

    else:
        # generator function (with a yield statement)
        @wraps(fixture_func, new_sig=new_sig)
        def wrapped_fixture_func(*args, **kwargs):
            """
            Decorator that returns a generator.

            Args:
            """
            request = kwargs['request'] if func_needs_request else kwargs.pop('request')
            if is_used_request(request):
                for res in fixture_func(*args, **kwargs):
                    yield res
            else:
                yield NOT_USED

    return wrapped_fixture_func


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
    # grab the caller module, so that we can later create the fixture directly inside it
    caller_module = get_caller_module()

    # test the `fixtures` argument to avoid common mistakes
    if not isinstance(fixtures, (tuple, set, list)):
        raise TypeError("fixture_union: the `fixtures` argument should be a tuple, set or list")

    # unpack the pytest.param marks
    custom_pids, p_marks, fixtures = extract_parameterset_info((name, ), fixtures)

    # get all required fixture names
    f_names = [get_fixture_name(f) for f in fixtures]

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

    union_fix = _fixture_union(caller_module, name,
                               fix_alternatives=fix_alternatives, unique_fix_alt_names=f_names_args,
                               scope=scope, idstyle=idstyle, ids=ids, autouse=autouse, hook=hook, **kwargs)

    # if unpacking is requested, do it here
    if unpack_into is not None:
        _make_unpack_fixture(caller_module, argnames=unpack_into, fixture=name, hook=hook)

    return union_fix


def _fixture_union(fixtures_dest,
                   name,                  # type: str
                   fix_alternatives,      # type: Sequence[UnionFixtureAlternative]
                   unique_fix_alt_names,  # type: List[str]
                   scope="function",      # type: str
                   idstyle="explicit",    # type: str
                   ids=None,              # type: Union[Callable, List[str]]
                   autouse=False,         # type: bool
                   hook=None,             # type: Callable[[Callable], Callable]
                   caller=fixture_union,  # type: Callable
                   **kwargs):
    """
    Internal implementation for fixture_union.
    The "alternatives" have to be created beforehand, by the caller. This allows `fixture_union` and `parametrize_plus`
    to use the same implementation while `parametrize_plus` uses customized "alternatives" containing more information.

    :param fixtures_dest:
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
    :param caller: a function to reference for error messages
    :param kwargs:
    :return:
    """
    if len(fix_alternatives) < 1:
        raise ValueError("Empty fixture unions are not permitted")

    # then generate the body of our union fixture. It will require all of its dependent fixtures and receive as
    # a parameter the name of the fixture to use
    @with_signature("%s(%s, request)" % (name, ', '.join(unique_fix_alt_names)))
    def _new_fixture(request, **all_fixtures):
        """
        Creates a new alternative.

        Args:
            request: (todo): write your description
            all_fixtures: (str): write your description
        """
        # ignore the "not used" marks, like in @ignore_unused
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
    _make_fix = pytest_fixture(scope=scope, params=fix_alternatives, autouse=autouse,
                               ids=ids or UnionIdMakers.get(idstyle), hook=hook, **kwargs)
    new_union_fix = _make_fix(_new_fixture)

    # Dynamically add fixture to caller's module as explained in https://github.com/pytest-dev/pytest/issues/2424
    check_name_available(fixtures_dest, name, if_name_exists=WARN, caller=caller)
    setattr(fixtures_dest, name, new_union_fix)

    return new_union_fix


_make_fixture_union = _fixture_union
"""A readable alias for callers not using the returned symbol"""


def unpack_fixture(argnames,  # type: str
                   fixture,   # type: Union[str, Callable]
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
    :param hook: an optional hook to apply to each fixture function that is created during this call. The hook function
        will be called everytime a fixture is about to be created. It will receive a single argument (the function
        implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from
        `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
    :return: the created fixtures.
    """
    # get caller module to create the symbols
    # todo what if this is called in a class ?
    caller_module = get_caller_module()
    return _unpack_fixture(caller_module, argnames, fixture, hook=hook)


def _unpack_fixture(fixtures_dest,  # type: ModuleType
                    argnames,       # type: Union[str, Iterable[str]]
                    fixture,        # type: Union[str, Callable]
                    hook            # type: Callable[[Callable], Callable]
                    ):
    """

    :param fixtures_dest:
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
        def _create_fixture(_value_idx):
            """
            Creates a function that creates a function that creates a function.

            Args:
                _value_idx: (str): write your description
            """
            # no need to autouse=True: this fixture does not bring any added value in terms of setup.
            @pytest_fixture(name=argname, scope=scope, autouse=False, hook=hook)
            @with_signature("%s(%s, request)" % (argname, source_f_name))
            def _param_fixture(request, **kwargs):
                """
                Extracts the value of the request.

                Args:
                    request: (todo): write your description
                """
                # ignore the "not used" marks, like in @ignore_unused
                if not is_used_request(request):
                    return NOT_USED
                # get the required fixture's value (the tuple to unpack)
                source_fixture_value = kwargs.pop(source_f_name)
                # unpack: get the item at the right position.
                return source_fixture_value[_value_idx]

            return _param_fixture

        # create it
        fix = _create_fixture(value_idx)

        # add to module
        check_name_available(fixtures_dest, argname, if_name_exists=WARN, caller=unpack_fixture)
        setattr(fixtures_dest, argname, fix)

        # collect to return the whole list eventually
        created_fixtures.append(fix)

    return created_fixtures


_make_unpack_fixture = _unpack_fixture
"""A readable alias for callers not using the returned symbol"""
