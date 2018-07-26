import sys
from abc import abstractmethod, ABC
from inspect import getmembers
from itertools import product
from typing import Callable, Union, Optional, Any, Tuple, List, Dict
from functools import lru_cache as lru

# noinspection PyBroadException
from warnings import warn

from pytest_cases.case_funcs import CaseData, ExpectedError, _GENERATOR_FIELD, CASE_TAGS_FIELD

try:
    from typing import Type
except:
    # on old versions of typing module the above does not work. Since our code below has all Type hints quoted it's ok
    pass

import pytest


class CaseDataGetter(ABC):
    """
    A proxy for a test case. Instances of this class are created by `@cases_data` or `extract_cases_from_module`.

    It provides a single method: `get(self, *args, **kwargs) -> CaseData`
    This method calls the actual underlying case with arguments propagation, and returns the result.

    The case functions can use the proposed standard `CaseData` type hint and return outputs matching this type hint,
    but this is not mandatory.
    """
    @abstractmethod
    def get(self, *args, **kwargs) -> Union[CaseData, Any]:
        """
        Retrieves the contents of the test case, with the provided arguments.
        :return:
        """

    def get_for(self, key) -> CaseData:
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


# Type hint for the simple functions
CaseFunc = Callable[[], CaseData]

# Type hint for generator functions
GeneratedCaseFunc = Callable[[Any], CaseData]


class CaseDataFromFunction(CaseDataGetter):
    """
    A CaseDataGetter relying on a function
    """

    def __init__(self, data_generator_func: Union[CaseFunc, GeneratedCaseFunc], case_name: str = None,
                 function_kwargs: Dict[str, Any] = None):
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
        return "Test Case Data generator - [" + self.f.__name__ + "] - " + str(self.f)

    def get(self, *args, **kwargs) -> Union[CaseData, Any]:
        """
        This implementation relies on the inner function to generate the case data.
        :return:
        """
        return self.f(*args, **kwargs, **self.function_kwargs)


CASE_PREFIX = 'case_'
"""Prefix used by default to identify case functions within a module"""

THIS_MODULE = object()
"""Marker that can be used instead of a module name to indicate that the module is the current one"""


def cases_data(cases=None, module=None, case_data_argname: str= 'case_data', has_tag: Any=None,
               filter: Callable[[List[Any]], bool]=None):
    """
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

    @cases_data(test_foo_cases)
    def test_foo(case_data: CaseData):
        ...
    ```

    is equivalent to:

    ```python
    import pytest
    from pytest_cases import extract_cases_from_module, CaseData

    # import the module containing the test cases
    import test_foo_cases

    # manually list the available cases
    cases = extract_cases_from_module(test_foo_cases)

    # parametrize the test function manually
    @pytest.mark.parametrize('case_data', cases, ids=str)
    def test_foo(case_data: CaseData):
        ...
    ```

    :param cases: a single case or a hardcoded list of cases to use. Only one of `cases` and `module` should be set.
    :param module: a module or a hardcoded list of modules to use. You may use `THIS_MODULE` to indicate that the
        module is the current one. Only one of `cases` and `module` should be set.
    :param case_data_argname: the optional name of the function parameter that should receive the `CaseDataGetter`
        object. Default is `case_data`.
    :param has_tag: an optional tag used to filter the cases. Only cases with the given tag will be selected. Only
        cases with the given tag will be selected.
    :param filter: an optional filtering function taking as an input a list of tags associated with a case, and
        returning a boolean indicating if the case should be selected. It will be used to filter the cases in the
        `module`. It both `has_tag` and `filter` are set, both will be applied in sequence.
    :return:
    """
    def datasets_decorator(test_func):
        """
        The generated test function decorator.

        It is equivalent to @mark.parametrize('case_data', cases) where cases is a tuple containing a CaseDataGetter for
        all case generator functions

        :param test_func:
        :return:
        """
        if module is not None and cases is not None:
            raise ValueError("Only one of module and cases should be provided")
        elif module is None:
            # Hardcoded sequence of cases, or single case
            if callable(cases):
                # single element
                _cases = [case_getter for case_getter in _get_case_getter_s(cases)]
            else:
                # already a sequence
                _cases = [case_getter for c in cases for case_getter in _get_case_getter_s(c)]
        else:
            # Gather all cases from the reference module(s)
            try:
                _cases = []
                for m in module:
                    m = sys.modules[test_func.__module__] if m is THIS_MODULE else m
                    _cases += extract_cases_from_module(m, has_tag=has_tag, filter=filter)
            except TypeError:
                # 'module' object is not iterable
                m = sys.modules[test_func.__module__] if module is THIS_MODULE else module
                _cases = extract_cases_from_module(m, has_tag=has_tag, filter=filter)

        # old: use id getter function : cases_ids = str
        # new: hardcode the case ids, safer (?) in case this is mixed with another fixture
        cases_ids = [str(c) for c in _cases]

        # Finally create the pytest decorator and apply it
        parametrizer = pytest.mark.parametrize(case_data_argname, _cases, ids=cases_ids)

        return parametrizer(test_func)

    return datasets_decorator


def _get_code(f):
    """
    Returns the source code associated to function f. It is robust to wrappers such as @lru_cache
    :param f:
    :return:
    """
    if hasattr(f, '__code__'):
        return f.__code__
    elif hasattr(f, '__wrapped__'):
        return _get_code(f.__wrapped__)
    else:
        raise ValueError("Cannot get code information for function " + str(f))


def extract_cases_from_module(module, has_tag: Any=None, filter: Callable[[List[Any]], bool]=None) \
        -> List[CaseDataGetter]:
    """
    Internal method used to create a list of `CaseDataGetter` for all cases available from the given module.
    See `@cases_data`

    :param module:
    :param has_tag: a tag used to filter the cases. Only cases with the given tag will be selected
    :param filter: a function taking as an input a list of tags associated with a case, and returning a boolean
        indicating if the case should be selected
    :return:
    """
    if filter is not None and not callable(filter):
        raise ValueError("`filter` should be a callable starting in pytest-cases 0.8.0. If you wish to provide a single"
                         " tag to match, use `has_tag` instead.")

    # First gather all case data providers in the reference module
    cases_dct = dict()
    for f_name, f in getmembers(module, callable):
        # only keep the functions
        #  - from the module file (not the imported ones),
        #  - starting with prefix 'case_'
        if f_name.startswith(CASE_PREFIX):
            code = _get_code(f)
            if code.co_filename == module.__file__:
                #  - with the optional filter/tag
                _tags = getattr(f, CASE_TAGS_FIELD, ())

                selected = True  # by default select the case, then AND the conditions
                if has_tag is not None:
                    selected = selected and (has_tag in _tags)
                if filter is not None:
                    selected = selected and filter(_tags)

                if selected:
                    # update the dictionary with the case getters
                    _get_case_getter_s(f, code, cases_dct)

    # convert into a list, taking all cases in order of appearance in the code (sort by source code line number)
    cases = [cases_dct[k] for k in sorted(cases_dct.keys())]

    return cases


def _get_case_getter_s(f, f_code=None, cases_dct=None) -> Optional[List[CaseDataFromFunction]]:
    """
    Creates the case function getter or the several cases function getters (in case of a generator) associated with
    function f. If cases_dct is provided, they are stored in this dictionary with a key equal to their code line number.
    For generated cases, a floating line number is created to preserve order.

    :param f:
    :param f_code: should be provided if cases_dct is provided.
    :param cases_dct: an optional dictionary where to store the created function wrappers
    :return:
    """

    # create a return variable if needed
    if cases_dct is None:
        cases_list = []
    else:
        cases_list = None

    # Handle case generators
    gen = getattr(f, _GENERATOR_FIELD, False)
    if gen:
        already_used_names = []

        name_template, param_ids, all_param_values_combinations = gen
        nb_cases_generated = len(all_param_values_combinations)

        for gen_case_id, case_params_values in enumerate(all_param_values_combinations):
            # build the dictionary of parameters for the case functions
            gen_case_params_dct = dict(zip(param_ids, case_params_values))

            # generate the case name by applying the name template
            gen_case_name = name_template.format(**gen_case_params_dct)
            if gen_case_name in already_used_names:
                raise ValueError("Generated function names for generator case function {} are not "
                                 "unique. Please use all parameter names in the string format variables"
                                 "".format(f.__name__))
            else:
                already_used_names.append(gen_case_name)
            case_getter = CaseDataFromFunction(f, gen_case_name, gen_case_params_dct)

            # save the result
            if cases_dct is None:
                cases_list.append(case_getter)
            else:
                # with an artificial floating point line number to keep order in dict
                gen_line_nb = f_code.co_firstlineno + (gen_case_id / nb_cases_generated)
                cases_dct[gen_line_nb] = case_getter
    else:
        # single case
        case_getter = CaseDataFromFunction(f)

        # save the result
        if cases_dct is None:
            cases_list.append(case_getter)
        else:
            cases_dct[f_code.co_firstlineno] = case_getter

    if cases_dct is None:
        return cases_list


def unfold_expected_err(expected_e: ExpectedError) -> Tuple[Optional['Type[Exception]'],
                                                            Optional[Exception],
                                                            Optional[Callable[[Exception], bool]]]:
    """
    'Unfolds' the expected error `expected_e` to return a tuple of
     - expected error type
     - expected error instance
     - error validation callable

    If `expected_e` is an exception type, returns `expected_e, None, None`
    If `expected_e` is an exception instance, returns `type(expected_e), expected_e, None`
    If `expected_e` is an exception validation function, returns `Exception, None, expected_e`

    :param expected_e: an `ExpectedError`, that is, either an exception type, an exception instance, or an exception
        validation function
    :return:
    """
    if type(expected_e) is type and issubclass(expected_e, Exception):
        return expected_e, None, None

    elif issubclass(type(expected_e), Exception):
        return type(expected_e), expected_e, None

    elif callable(expected_e):
        return Exception, None, expected_e

    raise ValueError("ExpectedNormal error should either be an exception type, an exception instance, or an exception "
                     "validation callable")
