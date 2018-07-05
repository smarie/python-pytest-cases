import sys
from abc import abstractmethod, ABC
from inspect import getmembers
from typing import Callable, Union, Optional, Any, Tuple, List

# noinspection PyBroadException
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


class CaseDataGetter(ABC):
    """
    Represents the contract that a test case dataset has to provide.
    It offers a single 'get()' method to get the contents of the test case
    """
    @abstractmethod
    def get(self) -> CaseData:
        """
        Getter for the contents of the tet case
        :return:
        """


# Type hint for the simple functions
DataGeneratorFunc = Callable[[], CaseData]


class CaseDataFromFunction(CaseDataGetter):
    """
    A CaseDataGetter relying on a function
    """
    def __init__(self, data_generator_func: DataGeneratorFunc):
        """

        :param data_generator_func:
        """
        self.f = data_generator_func

    def __str__(self):
        return self.f.__name__

    def __repr__(self):
        return "Test Case Data generator - [" + self.f.__name__ + "] - " + str(self.f)

    def get(self):
        """
        This implementation relies on the inner function to generate the dataset
        :return:
        """
        return self.f()


CASE_PREFIX = 'case_'


def cases_data(module, case_data_argname: str= 'case_data', filter: Any=None):
    """
    Decorates a test function so as to automatically parametrize it with all cases listed in module `module`.
    This functions

    :param module:
    :param case_data_argname: the name of the function parameter that should receive the `CaseDataGetter` object.
    Default is `case_data`
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
        # Gather all cases from the reference module
        if module is THIS_MODULE:
            cases = extract_cases_from_module(sys.modules[test_func.__module__], filter=filter)
        else:
            cases = extract_cases_from_module(module, filter=filter)

        # TODO if the function is already parametrized, combine this tuple with the existing one ? Actually not needed

        # Finally create the pytest decorator and apply it
        parametrizer = pytest.mark.parametrize(case_data_argname, cases, ids=str)

        return parametrizer(test_func)

    return datasets_decorator


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
        if f_name.startswith(CASE_PREFIX) \
                and f.__code__.co_filename == module.__file__:
            #  - with the optional filter tag
            if filter is None \
                    or hasattr(f, CASE_TAGS_FIELD) and filter in getattr(f, CASE_TAGS_FIELD):
                cases_dct[f.__code__.co_firstlineno] = f

    # convert into a tuple
    cases = [CaseDataFromFunction(cases_dct[k]) for k in sorted(cases_dct.keys())]

    return cases


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


def is_expected_error_instance(expected_e: ExpectedError) -> bool:
    """
    Returns true if the given argument is an exception instance

    :param expected_e:
    :return:
    """
    return issubclass(type(expected_e), Exception)


def assert_exception_equal(e: ExpectedError, expected_e: ExpectedError):
    """
    Utility method to assert that a received exception matches the expected one

    :param e:
    :param expected_e:
    :return:
    """
    if type(expected_e) is type:
        # compare types
        assert issubclass(type(e), expected_e)
    elif isinstance(expected_e, Exception):
        # compare instances
        assert e == expected_e
    elif callable(expected_e):
        # a callable to check if ok
        assert expected_e(e)
    else:
        raise TypeError("ExpectedNormal exception should either by an exception type or an exception instance, found: "
                        + str(expected_e))


THIS_MODULE = object()
