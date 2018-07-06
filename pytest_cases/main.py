import sys
from abc import abstractmethod, ABC
from inspect import getmembers
from itertools import product
from typing import Callable, Union, Optional, Any, Tuple, List, Dict
from functools import lru_cache as lru

# noinspection PyBroadException
from warnings import warn

try:
    from typing import Type
except:
    # on old versions of typing module the above does not work. Since our code below has all Type hints quoted it's ok
    pass

import pytest


# Type hints that you can use in your functions
Given = Any
ExpectedNormal = Optional[Any]
ExpectedError = Optional[Union['Type[Exception]', Exception, Callable[[Exception], Optional[bool]]]]
CaseData = Tuple[Given, ExpectedNormal, ExpectedError]


MultipleStepsCaseData = Tuple[Union[Given, Dict[str, Given]],
                              Union[ExpectedNormal, Dict[str, ExpectedNormal]],
                              Union[ExpectedError, Dict[str, ExpectedError]]]


class CaseDataGetter(ABC):
    """
    Represents the contract that a test case dataset has to provide.
    It offers a single 'get()' method to get the contents of the test case
    """
    @abstractmethod
    def get(self, *args, **kwargs) -> CaseData:
        """
        Getter for the contents of the tet case
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

    def get(self, *args, **kwargs) -> CaseData:
        """
        This implementation relies on the inner function to generate the dataset
        :return:
        """
        return self.f(*args, **kwargs, **self.function_kwargs)


def test_steps(*steps, test_step_argname: str= 'test_step'):
    """
    Decorates a test function so as to automatically parametrize it with all steps listed as arguments.

    When the steps are functions, this is equivalent to
    @pytest.mark.parametrize(test_step_argname, steps, ids=lambda x: x.__name__)

    :param steps:
    :return:
    """
    def steps_decorator(test_func):
        """
        The generated test function decorator.

        It is equivalent to @mark.parametrize('case_data', cases) where cases is a tuple containing a CaseDataGetter for
        all case generator functions

        :param test_func:
        :return:
        """
        def get_id(f):
            if callable(f) and hasattr(f, '__name__'):
                return f.__name__
            else:
                return str(f)

        # Finally create the pytest decorator and apply it
        parametrizer = pytest.mark.parametrize(test_step_argname, steps, ids=get_id)
        return parametrizer(test_func)

    return steps_decorator


test_steps.__test__ = False  # to prevent pytest to think that this is a test !


CASE_PREFIX = 'case_'


def cases_data(case_data_argname: str= 'case_data', cases=None, module=None, filter: Any=None):
    """
    Decorates a test function so as to automatically parametrize it with all cases listed in module `module`, or with
    all cases listed explicitly in `cases`.

    Using it with a non-None `module` argument is equivalent to
     * extracting all cases from module
     * then decorating your function with @pytest.mark.parametrize

    You can perform the two steps manually with:

    ```python
    import pytest
    from pytest_cases import extract_cases_from_module, CaseData

    # import the module containing the test cases
    import test_foo_cases

    # manually list the available cases
    cases = extract_cases_from_module(test_foo_cases)

    # parametrize the test function manually
    @pytest.mark.parametrize('case_data', cases, ids=str)
    def test_with_cases_decorated(case_data: CaseData):
        ...
    ```

    :param case_data_argname: the name of the function parameter that should receive the `CaseDataGetter` object.
        Default is `case_data`.
    :param cases: a case or hardcoded list of cases to use. This can not be used together with `module`
    :param module: a module or hardcoded list of modules to use. This can not be used together with `module`
    :param filter: a tag used to filter the cases. Only cases with the given tag will be selected
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
                _cases = (case_getter for case_getter in get_case_getter_s(cases))
            else:
                # already a sequence
                _cases = (case_getter for c in cases for case_getter in get_case_getter_s(c))
        else:
            # Gather all cases from the reference module(s)
            try:
                _cases = []
                for m in module:
                    m = sys.modules[test_func.__module__] if m is THIS_MODULE else m
                    _cases += extract_cases_from_module(m, filter=filter)
            except TypeError:
                # 'module' object is not iterable
                m = sys.modules[test_func.__module__] if module is THIS_MODULE else module
                _cases = extract_cases_from_module(m, filter=filter)

        # Finally create the pytest decorator and apply it
        parametrizer = pytest.mark.parametrize(case_data_argname, _cases, ids=str)

        return parametrizer(test_func)

    return datasets_decorator


def get_code(f):
    """
    Returns the source code associated to function f. It is robust to wrappers such as @lru_cache
    :param f:
    :return:
    """
    if hasattr(f, '__code__'):
        return f.__code__
    elif hasattr(f, '__wrapped__'):
        return get_code(f.__wrapped__)
    else:
        raise ValueError("Cannot get code information for function " + str(f))


def extract_cases_from_module(module, filter: Any=None) -> List[CaseDataGetter]:
    """
    Internal method used to create all cases available from the given module

    :param module:
    :param filter: a tag used to filter the cases. Only cases with the given tag will be selected
    :return:
    """
    # First gather all case data providers in the reference module
    cases_dct = dict()
    for f_name, f in getmembers(module, callable):
        # only keep the functions
        #  - from the module file (not the imported ones),
        #  - starting with prefix 'case_'
        if f_name.startswith(CASE_PREFIX):
            code = get_code(f)
            if code.co_filename == module.__file__:
                #  - with the optional filter tag
                if filter is None \
                        or hasattr(f, CASE_TAGS_FIELD) and filter in getattr(f, CASE_TAGS_FIELD):

                    # update the dictionary with the case getters
                    get_case_getter_s(f, code, cases_dct)

    # convert into a list, taking all cases in order of appearance in the code (sort by source code line number)
    cases = [cases_dct[k] for k in sorted(cases_dct.keys())]

    return cases


def get_case_getter_s(f, f_code=None, cases_dct=None) -> Optional[List[CaseDataFromFunction]]:
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
    gen = getattr(f, GENERATOR_FIELD, False)
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


def case_name(name: str):
    """
    Decorator to simply change the name of a case generator function

    :param name: the name that will be used in the test case, instead of the case generator function name
    :return:
    """
    def case_name_decorator(test_func):
        test_func.__name__ = name
        return test_func

    return case_name_decorator


CASE_TAGS_FIELD = '__case_tags__'


def case_tags(*tags: Any):
    """
    Decorator to tag a case function with a list of tags.
    Tags can be used in the @cases_data test function decorator to specify cases within a module, that should be applied

    :param tags: a list of tags to decorate this case.
    :return:
    """
    def case_tags_decorator(test_func):
        existing_tags = getattr(test_func, CASE_TAGS_FIELD, None)
        if existing_tags is None:
            # there are no tags yet. Use the provided
            setattr(test_func, CASE_TAGS_FIELD, list(tags))
        else:
            # there are some tags already, let's try to add the new to the existing
            setattr(test_func, CASE_TAGS_FIELD, existing_tags + list(tags))
        return test_func

    return case_tags_decorator


def test_target(target: Any):
    """
    A simple decorator to declare that a case function is associated with a particular target.

    >>> @test_target(int)
    >>> def case_to_test_int():
    >>>     ...

    This is actually an alias for `@case_tags(target)`, but it is a bit more readable

    :param target: for example a function, a class... or a string representing a function, a class...
    :return:
    """
    return case_tags(target)


test_target.__test__ = False  # disable this function in pytest (otherwise name starts with 'test' > it will appear)


def unfold_expected_err(expected_e: ExpectedError) -> Tuple[Optional['Type[Exception]'],
                                                            Optional[Exception],
                                                            Optional[Callable[[Exception], bool]]]:
    """
    'Unfolds' the expected error to return a tuple of
     - expected error type
     - expected error instance
     - error validation callable

    :param expected_e:
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


THIS_MODULE = object()


GENERATOR_FIELD = '__cases_generator__'


def cases_generator(name_template, lru_cache=False, **kwargs):
    """
    Decorator to declare a case function as being a cases generator.

    >>> @cases_generator("test with i={i}", i=range(10))
    >>> def case_10_times(i):
    >>>     ''' Generates 10 cases '''
    >>>     ins = dict(a=i, b=i+1)
    >>>     outs = i+1, i+2
    >>>     return ins, outs, None

    :return:
    """

    def cases_generator_decorator(test_func):
        kwarg_values = list(product(*kwargs.values()))
        setattr(test_func, GENERATOR_FIELD, (name_template, kwargs.keys(), kwarg_values))
        if lru_cache:
            nb_cases = len(kwarg_values)
            # decorate the function
            test_func = lru(maxsize=nb_cases)(test_func)

        return test_func

    return cases_generator_decorator
