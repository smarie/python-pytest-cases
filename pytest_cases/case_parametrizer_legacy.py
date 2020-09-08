# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
# Use true division operator always even in old python 2.x (used in `_get_case_getter_s`)
from __future__ import division

import sys
from abc import abstractmethod, ABCMeta
from decopatch import function_decorator, DECORATED, with_parenthesis
from warnings import warn

try:  # python 3.3+
    from inspect import signature, Parameter
except ImportError:
    from funcsigs import signature, Parameter  # noqa

import pytest

try:  # type hints, python 3+
    from typing import Type, Callable, Union, Optional, Any, Tuple, List, Dict, Iterable  # noqa
    from pytest_cases.case_funcs_legacy import CaseData, ExpectedError  # noqa
    from types import ModuleType  # noqa

    # Type hint for the simple functions
    CaseFunc = Callable[[], CaseData]

    # Type hint for generator functions
    GeneratedCaseFunc = Callable[[Any], CaseData]
except:  # noqa
    pass

from .common_mini_six import with_metaclass, string_types
from .common_pytest_marks import get_pytest_marks_on_function, make_marked_parameter_value

from .case_funcs_legacy import is_case_generator, get_case_generator_details
from .case_funcs_new import matches_tag_query
from .case_parametrizer_new import THIS_MODULE, extract_cases_from_module

from .fixture_core2 import fixture_plus


class CaseDataGetter(with_metaclass(ABCMeta)):
    """ DEPRECATED - this was created in v1 only by `@cases_data` (not by v2 `@parametrize_with_cases`)

    A proxy for a test case. Instances of this class are created by `@cases_data` or `get_all_cases`.

    It provides a single method: `get(self, *args, **kwargs) -> CaseData`
    This method calls the actual underlying case with arguments propagation, and returns the result.

    The case functions can use the proposed standard `CaseData` type hint and return outputs matching this type hint,
    but this is not mandatory.
    """
    @abstractmethod
    def get(self, *args, **kwargs):
        # type: (...) -> Union[CaseData, Any]
        """
        Retrieves the contents of the test case, with the provided arguments.
        :return:
        """

    def get_marks(self):
        """
        Returns the pytest marks on this case, if any
        :return:
        """
        return []

    def get_for(self, key):
        # type: (...) -> CaseData
        """
        DEPRECATED as it is hardcoded for a very particular format of case data. Please rather use get() directly, and
        do the selection in the results yourself based on your case data format.
        ---
        Returns a new case data getter where the data is automatically filtered with the key.
        This only works if the function returns a `MultipleStepsCaseData`
        :return:
        """
        warn("This method is deprecated, as it is hardcoded for a very particular format of case data. Please rather"
             "use get() directly, and do the selection in the results yourself based on your case data format",
             category=DeprecationWarning, stacklevel=2)

        data = self.get()

        # assume that the data is a MultiStepsCaseData = a tuple with 3 items and the second and third are dict or None
        ins = data[0]
        outs = None if data[1] is None else data[1][key]
        err = None if data[2] is None else data[2][key]

        return ins, outs, err


class CaseDataFromFunction(CaseDataGetter):
    """ DEPRECATED - this was created in v1 only by `@cases_data` (not by v2 `@parametrize_with_cases`)

    A CaseDataGetter relying on a function
    """

    def __init__(self, data_generator_func,  # type: Union[CaseFunc, GeneratedCaseFunc]
                 case_name=None,             # type: str
                 function_kwargs=None        # type: Dict[str, Any]
                 ):
        """

        :param data_generator_func:
        """
        self.f = data_generator_func
        self.case_name = case_name
        if function_kwargs is None:
            function_kwargs = dict()
        self.function_kwargs = function_kwargs

    def __str__(self):
        if self.case_name is not None:
            return self.case_name
        else:
            return self.f.__name__

    def __repr__(self):
        return "Test Case Data generator - [" + str(self) + "] - " + str(self.f)

    def get_marks(self):
        """
        Overrides default implementation to return the marks that are on the case function
        :return:
        """
        return get_pytest_marks_on_function(self.f)

    def get(self, *args, **kwargs):
        # type: (...) -> Union[CaseData, Any]
        """
        This implementation relies on the inner function to generate the case data.
        :return:
        """
        kwargs.update(self.function_kwargs)
        return self.f(*args, **kwargs)


@function_decorator(custom_disambiguator=with_parenthesis)
def cases_data(cases=None,                       # type: Union[Callable[[Any], Any], Iterable[Callable[[Any], Any]]]
               module=None,                      # type: Union[ModuleType, Iterable[ModuleType]]
               case_data_argname='case_data',    # type: str
               has_tag=None,                     # type: Any
               filter=None,                      # type: Callable[[List[Any]], bool]  # noqa
               test_func=DECORATED,  # noqa
               ):
    """ DEPRECATED (V1) - use V2 `@parametrize_with_cases(argnames, ...)`

    Decorates a test function so as to automatically parametrize it with all cases listed in module `module`, or with
    all cases listed explicitly in `cases`.

    Using it with a non-None `module` argument is equivalent to
     * extracting all cases from `module`
     * then decorating your function with @pytest.mark.parametrize with all the cases

    So

    ```python
    from pytest_cases import cases_data, CaseData

    # import the module containing the test cases
    import test_foo_cases

    @cases_data(module=test_foo_cases)
    def test_foo(case_data: CaseData):
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

    # parametrize the test function manually
    @pytest.mark.parametrize('case_data', cases, ids=str)
    def test_foo(case_data: CaseData):
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
    warn("`@cases_data` is deprecated. Please use `@parametrize_with_cases`.", category=DeprecationWarning,
         stacklevel=2)

    # equivalent to @mark.parametrize('case_data', cases) where cases is a tuple containing a CaseDataGetter for

    # First list all cases according to user preferences
    _cases = get_all_cases_legacy(cases, module, test_func, has_tag, filter)

    # Then transform into required arguments for pytest (applying the pytest marks if needed)
    marked_cases, cases_ids = get_pytest_parametrize_args_legacy(_cases)

    # Finally create the pytest decorator and apply it
    parametrizer = pytest.mark.parametrize(case_data_argname, marked_cases, ids=cases_ids)

    return parametrizer(test_func)


def get_pytest_parametrize_args_legacy(cases):
    """
    Transforms a list of cases into a tuple containing the arguments to use in `@pytest.mark.parametrize`
    the tuple is (marked_cases, ids) where

     - marked_cases is a list containing either the case or a pytest-marked case (using the pytest marks that were
     present on the case function)
     - ids is a list containing the case ids to use as test ids.

    :param cases:
    :return: (marked_cases, ids)
    """
    # hardcode the case ids, as simply passing 'ids=str' would not work when cases are marked cases
    case_ids = [str(c) for c in cases]

    # create the pytest parameter values with the appropriate pytest marks
    marked_cases = [c if len(c.get_marks()) == 0 else make_marked_parameter_value((c,), marks=c.get_marks())
                    for c in cases]

    return marked_cases, case_ids


def get_all_cases_legacy(cases=None,               # type: Union[Callable[[Any], Any], Iterable[Callable[[Any], Any]]]
                         module=None,              # type: Union[ModuleType, Iterable[ModuleType]]
                         this_module_object=None,  # type: Any
                         has_tag=None,             # type: Any
                         filter=None               # type: Callable[[List[Any]], bool]  # noqa
                         ):
    # type: (...) -> List[CaseDataGetter]
    """
    Lists all desired cases from the user inputs. This function may be convenient for debugging purposes.

    :param cases: a single case or a hardcoded list of cases to use. Only one of `cases` and `module` should be set.
    :param module: a module or a hardcoded list of modules to use. You may use `THIS_MODULE` to indicate that the
        module is the current one. Only one of `cases` and `module` should be set.
    :param this_module_object: any variable defined in the module of interest, for example a function. It is used to
        find "this module", when `module` contains `THIS_MODULE`.
    :param has_tag: an optional tag used to filter the cases. Only cases with the given tag will be selected. Only
        cases with the given tag will be selected.
    :param filter: an optional filtering function taking as an input a list of tags associated with a case, and
        returning a boolean indicating if the case should be selected. It will be used to filter the cases in the
        `module`. It both `has_tag` and `filter` are set, both will be applied in sequence.
    :return:
    """
    _facto = _get_case_getter_s(has_tag=has_tag, filter=filter)
    _cases = None

    if module is not None and cases is not None:
        raise ValueError("Only one of module and cases should be provided")

    elif module is None:
        # Hardcoded sequence of cases, or single case
        if callable(cases):
            # single element
            _cases = [case_getter for case_getter in _facto(cases)]
        elif cases is THIS_MODULE:
            raise ValueError("`THIS_MODULE` should only be used in the `module` argument, not in the `cases` argument")
        else:
            # already a sequence
            _cases = [case_getter for c in cases for case_getter in _facto(c)]
    else:
        # Gather all cases from the reference module(s)
        try:
            _cases = []
            for m in module:  # noqa
                m = sys.modules[this_module_object.__module__] if m is THIS_MODULE else m
                _cases += extract_cases_from_module(m, _case_param_factory=_facto)
            success = True
        except TypeError:
            success = False

        if not success:
            # 'module' object is not iterable: a single module was provided
            m = sys.modules[this_module_object.__module__] if module is THIS_MODULE else module
            _cases = extract_cases_from_module(m, _case_param_factory=_facto)

    return _cases


class InvalidNamesTemplateException(Exception):
    """
    Raised when a `@cases_generator` is used with an improper name template and formatting fails.
    """
    def __init__(self, cases_func, names_template, params):
        self.cases_func = cases_func
        self.names_template = names_template
        self.params = params
        super(InvalidNamesTemplateException, self).__init__()

    def __str__(self):
        return "Error creating the case name for case generator <%s> using name template '%s' with parameter values " \
               "%s. Please check the name template." % (self.cases_func.__name__, self.names_template, self.params)


def _get_case_getter_s(has_tag=None, filter=None):
    if filter is not None and not callable(filter):
        raise ValueError("`filter` should be a callable starting in pytest-cases 0.8.0. If you wish to provide a single"
                         " tag to match, use `has_tag` instead.")

    def __get_case_getter_s(f,
                            co_firstlineno=None,
                            cases_dct=None):
        # type: (...) -> Optional[List[CaseDataFromFunction]]
        """
        Creates the case function getter or the several cases function getters (in case of a generator) associated with
        function f. If cases_dct is provided, they are stored in this dictionary with a key equal to their code line number.
        For generated cases, a floating line number is created to preserve order.

        :param f:
        :param co_firstlineno: should be provided if cases_dct is provided.
        :param cases_dct: an optional dictionary where to store the created function wrappers
        :return:
        """
        # create a return variable if needed
        if cases_dct is None:
            cases_list = []
        else:
            cases_list = None

        if matches_tag_query(f, has_tag=has_tag, filter=filter):
            # Handle case generators
            if is_case_generator(f):
                already_used_names = []

                names, param_ids, all_param_values_combinations = get_case_generator_details(f)
                nb_cases_generated = len(all_param_values_combinations)

                if names is None:
                    # default template based on parameter names
                    names = "%s__%s" % (f.__name__, ', '.join("%s={%s}" % (p_name, p_name) for p_name in param_ids))

                if isinstance(names, string_types):
                    # then this is a string formatter creating the names. Create the corresponding callable
                    _formatter = names

                    def names(**params):
                        try:
                            return _formatter.format(**params)
                        except Exception:
                            raise InvalidNamesTemplateException(f, _formatter, params)

                if not callable(names):
                    # This is an explicit list
                    if len(names) != nb_cases_generated:
                        raise ValueError("An explicit list of names has been provided but it has not the same length (%s) than"
                                         " the number of cases to be generated (%s)" % (len(names), nb_cases_generated))

                for gen_case_id, case_params_values in enumerate(all_param_values_combinations):
                    # build the dictionary of parameters for the case functions
                    gen_case_params_dct = dict(zip(param_ids, case_params_values))

                    # generate the case name by applying the name template
                    if callable(names):
                        gen_case_name = names(**gen_case_params_dct)
                    else:
                        # an explicit list is provided
                        gen_case_name = names[gen_case_id]

                    if gen_case_name in already_used_names:
                        raise ValueError("Generated function names for generator case function {} are not "
                                         "unique. Please use all parameter names in the string format variables"
                                         "".format(f.__name__))
                    else:
                        already_used_names.append(gen_case_name)
                    case_getter = CaseDataFromFunction(f, gen_case_name, gen_case_params_dct)

                    # save the result in the list or the dict
                    if cases_dct is None:
                        cases_list.append(case_getter)
                    else:
                        # with an artificial floating point line number to keep order in dict
                        gen_line_nb = co_firstlineno + (gen_case_id / nb_cases_generated)
                        cases_dct[gen_line_nb] = case_getter
            else:
                # single case
                case_getter = CaseDataFromFunction(f)

                # save the result
                if cases_dct is None:
                    cases_list.append(case_getter)
                else:
                    cases_dct[co_firstlineno] = case_getter

        if cases_dct is None:
            return cases_list

    return __get_case_getter_s


@function_decorator
def cases_fixture(cases=None,                       # type: Union[Callable[[Any], Any], Iterable[Callable[[Any], Any]]]
                  module=None,                      # type: Union[ModuleType, Iterable[ModuleType]]
                  case_data_argname='case_data',    # type: str
                  has_tag=None,                     # type: Any
                  filter=None,                      # type: Callable[[List[Any]], bool] # noqa
                  f=DECORATED,  # noqa
                  **kwargs
                  ):
    """ DEPRECATED - use double annotation `@fixture_plus` + `@parametrize_with_cases` instead

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
    warn("`@cases_fixture` is deprecated. Please use `@fixture_plus` with `@parametrize_with_cases(id=<name>)` (V2) "
         "or `@cases_data` (V1).", category=DeprecationWarning, stacklevel=2)

    # apply @cases_data (that will translate to a @pytest.mark.parametrize)
    parametrized_f = cases_data(cases=cases, module=module,
                                case_data_argname=case_data_argname, has_tag=has_tag, filter=filter)(f)
    # apply @fixture_plus
    return fixture_plus(**kwargs)(parametrized_f)
