from collections import Iterable
from inspect import isgeneratorfunction
from warnings import warn

try:  # python 3.3+
    from inspect import signature, Parameter
except ImportError:
    from funcsigs import signature, Parameter  # noqa

try:
    from typing import Union, Callable, List, Any  # noqa
except ImportError:
    pass

import pytest
from makefun import with_signature, remove_signature_parameters, add_signature_parameters, wraps

from .common_pytest import get_fixture_name, remove_duplicates, is_marked_parameter_value, mini_idvalset, \
    get_param_argnames_as_list, extract_parameterset_info

from .fixture__creation import check_name_available, CHANGE, WARN, get_caller_module
from .fixture_core1_unions import InvalidParamsList, NOT_USED, UnionFixtureAlternative, _make_fixture_union, \
    _make_unpack_fixture
from .fixture_core2 import _create_param_fixture, fixture_plus


def _fixture_product(caller_module,
                     name,                # type: str
                     fixtures_or_values,
                     fixture_positions,
                     scope="function",    # type: str
                     ids=None,            # type: Union[Callable, List[str]]
                     unpack_into=None,    # type: Iterable[str]
                     autouse=False,       # type: bool
                     hook=None,           # type: Callable[[Callable], Callable]
                     caller=None,         # type: Callable
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
    check_name_available(caller_module, name, if_name_exists=WARN, caller=caller)
    setattr(caller_module, name, fix)

    # if unpacking is requested, do it here
    if unpack_into is not None:
        _make_unpack_fixture(caller_module, argnames=unpack_into, fixture=name, hook=hook)

    return fix


_make_fixture_product = _fixture_product
"""A readable alias for callers not using the returned symbol"""


class fixture_ref:  # noqa
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

        :param style:
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

        def _make_idfun_for_params(argnames,  # noqa
                                   nb_positions):
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
            def _tmp_make_id(argvals):
                _tmp_make_id.i += 1
                if _tmp_make_id.i >= nb_positions:
                    raise ValueError("Internal error, please report")
                argvals = argvals if len(argnames) > 1 else (argvals,)
                return mini_idvalset(argnames, argvals, idx=_tmp_make_id.i)

            # init its positions counter
            _tmp_make_id.i = -1
            return _tmp_make_id

        def _create_params_alt(test_func_name, union_name, from_i, to_i, hook):  # noqa
            """ Routine that will be used to create a parameter fixture for argvalues between prev_i and i"""

            single_param = (to_i == from_i + 1)

            if single_param:
                i = from_i  # noqa

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

        def _create_fixture_ref_alt(union_name, i):  # noqa
            # Get the referenced fixture name
            f_fix_name = get_fixture_name(argvalues[i].fixture)

            # Create the alternative
            f_fix_alt = FixtureParamAlternative(union_name=union_name, alternative_name=f_fix_name,
                                                argnames=argnames, argvalues_index=i)
            # Finally copy the custom id/marks on the ParamAlternative if any
            if is_marked_parameter_value(marked_argvalues[i]):
                f_fix_alt = pytest.param(f_fix_alt, id=marked_argvalues[i].id, marks=marked_argvalues[i].marks)

            return f_fix_name, f_fix_alt

        def _create_fixture_ref_product(union_name, i, fixture_ref_positions, test_func_name, hook):  # noqa

            # If an explicit list of ids was provided, slice it. Otherwise use the provided callable
            try:
                p_ids = ids[i]
            except TypeError:
                p_ids = ids  # callable

            # values to use:
            p_values = argvalues[i]

            # Create a unique fixture name
            p_fix_name = "%s_%s_P%s" % (test_func_name, param_names_str, i)
            p_fix_name = check_name_available(caller_module, p_fix_name, if_name_exists=CHANGE, caller=parametrize_plus)

            # Create the fixture
            _make_fixture_product(caller_module, name=p_fix_name, hook=hook, ids=p_ids, fixtures_or_values=p_values,
                                  fixture_positions=fixture_ref_positions, caller=parametrize_plus)

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

            # Are there explicit ids provided ?
            try:
                if len(ids) != len(argvalues):
                    raise ValueError("Explicit list of `ids` provided has a different length (%s) than the number of "
                                     "parameter sets (%s)" % (len(ids), len(argvalues)))
                explicit_ids_to_use = []
            except TypeError:
                explicit_ids_to_use = None

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
            for i, j_list in fixture_indices:  # noqa
                # A/ Is there any non-empty group of 'normal' parameters before the fixture_ref at <i> ? If so, handle.
                if i > prev_i + 1:
                    # create a new "param" fixture parametrized with all of that consecutive group.
                    # Important note: we could either wish to create one fixture for parameter value or to create
                    #  one for each consecutive group as shown below. This should not lead to different results but perf
                    #  might differ. Maybe add a parameter in the signature so that users can test it ?
                    #  this would make the ids more readable by removing the "P2toP3"-like ids
                    p_fix_name, p_fix_alt = _create_params_alt(test_func_name=test_func_name, hook=hook,
                                                               union_name=fixture_union_name, from_i=prev_i + 1, to_i=i)
                    fixture_alternatives.append((p_fix_name, p_fix_alt))
                    if explicit_ids_to_use is not None:
                        if isinstance(p_fix_alt, SingleParamAlternative):
                            explicit_ids_to_use.append(ids[prev_i + 1])
                        else:
                            # the ids provided by the user are propagated to the params of this fix, so we need an id
                            explicit_ids_to_use.append(ParamIdMakers.explicit(p_fix_alt))

                # B/ Now handle the fixture ref at position <i>
                if j_list is None:
                    # argvalues[i] contains a single argvalue that is a fixture_ref : add the referenced fixture
                    f_fix_name, f_fix_alt = _create_fixture_ref_alt(union_name=fixture_union_name, i=i)
                    fixture_alternatives.append((f_fix_name, f_fix_alt))
                    if explicit_ids_to_use is not None:
                        explicit_ids_to_use.append(ids[i])

                else:
                    # argvalues[i] is a tuple, some of them being fixture_ref. create a fixture refering to all of them
                    prod_fix_name, prod_fix_alt = _create_fixture_ref_product(union_name=fixture_union_name, i=i,
                                                                              fixture_ref_positions=j_list,
                                                                              test_func_name=test_func_name, hook=hook)
                    fixture_alternatives.append((prod_fix_name, prod_fix_alt))
                    if explicit_ids_to_use is not None:
                        explicit_ids_to_use.append(ids[i])

                prev_i = i

            # C/ handle last consecutive group of normal parameters, if any
            i = len(argvalues)  # noqa
            if i > prev_i + 1:
                p_fix_name, p_fix_alt = _create_params_alt(test_func_name=test_func_name, union_name=fixture_union_name,
                                                           from_i=prev_i + 1, to_i=i, hook=hook)
                fixture_alternatives.append((p_fix_name, p_fix_alt))
                if explicit_ids_to_use is not None:
                    if isinstance(p_fix_alt, SingleParamAlternative):
                        explicit_ids_to_use.append(ids[prev_i + 1])
                    else:
                        # the ids provided by the user are propagated to the params of this fix, so we need an id
                        explicit_ids_to_use.append(ParamIdMakers.explicit(p_fix_alt))

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

            # note: the function automatically registers it in the module
            _make_fixture_union(caller_module, name=fixture_union_name, hook=hook, caller=parametrize_plus,
                                fix_alternatives=fix_alternatives, unique_fix_alt_names=fix_alt_names,
                                ids=explicit_ids_to_use or ids or ParamIdMakers.get(idstyle))

            # --create the new test function's signature that we want to expose to pytest
            # it is the same than existing, except that we want to replace all parameters with the new fixture
            # first check where we should insert the new parameters (where is the first param we remove)
            _first_idx = -1
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
            def replace_paramfixture_with_values(kwargs):  # noqa
                # remove the created fixture value
                encompassing_fixture = kwargs.pop(fixture_union_name)
                # and add instead the parameter values
                if nb_params > 1:
                    for i, p in enumerate(argnames):  # noqa
                        kwargs[p] = encompassing_fixture[i]
                else:
                    kwargs[argnames[0]] = encompassing_fixture
                # return
                return kwargs

            if not isgeneratorfunction(test_func):
                # normal test function with return statement
                @wraps(test_func, new_sig=new_sig)
                def wrapped_test_func(*args, **kwargs):  # noqa
                    if kwargs.get(fixture_union_name, None) is NOT_USED:
                        # TODO why this ?
                        return NOT_USED
                    else:
                        replace_paramfixture_with_values(kwargs)
                        return test_func(*args, **kwargs)

            else:
                # generator test function (with one or several yield statements)
                @wraps(test_func, new_sig=new_sig)
                def wrapped_test_func(*args, **kwargs):  # noqa
                    if kwargs.get(fixture_union_name, None) is NOT_USED:
                        # TODO why this ?
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
