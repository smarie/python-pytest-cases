from abc import ABCMeta, abstractmethod
from inspect import getmembers
from typing import Callable, Union, Optional, Any, Tuple

import pytest

CASE_PREFIX = 'case_'


def cases_data(module, case_data_argname: str= 'case_data'):
    """
    Decorates a test function so as to automatical

    :param test_func:
    :param file:
    :param case_data_argname:
    :return:
    """
    def datasets_decorator(test_func):
        """
        The generated test function decorator.

        It is equivalent to @mark.parametrize('case_data', cases) where cases is a tuple containing a CaseData for
        all case generator functions

        :param test_func:
        :return:
        """
        # Gather all cases from the reference module
        cases = extract_cases_from_module(module)

        # TODO if the function is already parametrized, combine this tuple with the existing one ? Actually not needed

        # Finally create the pytest decorator and apply it
        parametrizer = pytest.mark.parametrize(case_data_argname, cases, ids=str)

        return parametrizer(test_func)

    return datasets_decorator


def extract_cases_from_module(module):
    """
    Internal method used to create all cases available from the given module

    :param module:
    :return:
    """
    # First gather all case data providers in the reference module
    cases_dct = dict()
    for f_name, f in getmembers(module, callable):
        # only keep the functions from the module file (not the imported ones), starting with prefix 'case_'
        if f_name.startswith(CASE_PREFIX) and f.__code__.co_filename == module.__file__:
            # TODO AND relates to test_func
            # cases_dct[f_name] = f
            cases_dct[f.__code__.co_firstlineno] = f

    # convert into a tuple
    cases = [CaseDataFromFunction(cases_dct[k]) for k in sorted(cases_dct.keys())]

    return cases


def case_name(name: str):
    """
    Decorator to simply change the name of a case provider function

    :param test_func:
    :return:
    """
    def case_name_decorator(test_func):
        test_func.__name__ = name
        return test_func

    return case_name_decorator


# Type hints that you can use in your functions
Given = Any
ExpectedNormal = Optional[Any]
ExpectedError = Optional[Union['Type[Exception]', Exception, Callable[[Exception], bool]]]


class CaseData(metaclass=ABCMeta):
    """
    Represents the contract that a test case dataset has to provide.
    It offers a single 'get()' method to get the contents of the test case
    """
    @abstractmethod
    def get(self) -> Tuple[Given, ExpectedNormal, ExpectedError]:
        """
        Getter for the contents of the tet case
        :return:
        """


# Type hint for the simple functions
DataGeneratorFunc = Callable[[], Tuple[Given, ExpectedNormal, ExpectedError]]


class CaseDataFromFunction(CaseData):
    """
    A CaseData relying on a function
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
