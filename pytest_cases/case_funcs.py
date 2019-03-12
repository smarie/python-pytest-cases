from __future__ import division

from decopatch import DECORATED, function_decorator, with_parenthesis

try:  # python 3.2+
    from functools import lru_cache as lru
except ImportError:
    from functools32 import lru_cache as lru

from itertools import product

try:  # python 3.5+
    from typing import Callable, Union, Optional, Any, Tuple, Dict, Iterable

    # Type hints that you can use in your functions
    Given = Any
    """The input(s) for the test. It can be anything"""

    ExpectedNormal = Optional[Any]
    """The expected test results in case success is expected, or None if this test should fail"""

    ExpectedError = Optional[Union['Type[Exception]', Exception, Callable[[Exception], Optional[bool]]]]
    """The expected error in case failure is expected, or None if the test should succeed. It is proposed that expected 
    error can be defined as an exception type, an exception instance, or an exception validation function"""

    CaseData = Tuple[Given, ExpectedNormal, ExpectedError]

    MultipleStepsCaseData = Tuple[Union[Given, Dict[Any, Given]],
                                  Union[ExpectedNormal, Dict[Any, ExpectedNormal]],
                                  Union[ExpectedError, Dict[Any, ExpectedError]]]
except:
    pass

try:  # python 3.5.4+
    from typing import Type
except:
    # on old versions of typing module the above does not work. Since our code below has all Type hints quoted it's ok
    pass


_GENERATOR_FIELD = '__cases_generator__'
"""Internal marker used for cases generators"""


@function_decorator
def case_name(name,  # type: str
              test_func=DECORATED
              ):
    """
    Decorator to override the name of a case function. The new name will be used instead of the function name,
    in test names.

    ```python
    @case_name('simple_case')
    def case_simple():
        ...
    ```

    :param name: the name that will be used in the test case instead of the case function name
    :return:
    """
    test_func.__name__ = name
    return test_func


CASE_TAGS_FIELD = '__case_tags__'


@function_decorator(custom_disambiguator=with_parenthesis)
def case_tags(*tags  # type: Any
              ):
    """
    Decorator to tag a case function with a list of tags. These tags can then be used in the `@cases_data` test
    function decorator to filter cases within the selected module(s).

    :param tags: a list of tags that may be used to filter the case. Tags can be anything (string, objects, types,
        functions...)
    :return:
    """
    # we have to use "nested" mode for this decorator because in the decorator signature we have a var-positional
    def _apply(case_func):
        existing_tags = getattr(case_func, CASE_TAGS_FIELD, None)
        if existing_tags is None:
            # there are no tags yet. Use the provided
            setattr(case_func, CASE_TAGS_FIELD, list(tags))
        else:
            # there are some tags already, let's try to add the new to the existing
            setattr(case_func, CASE_TAGS_FIELD, existing_tags + list(tags))
        return case_func

    return _apply


def test_target(target  # type: Any
                ):
    """
    A simple decorator to declare that a case function is associated with a particular target.

    >>> @test_target(int)
    >>> def case_to_test_int():
    >>>     ...

    This is actually an alias for `@case_tags(target)`, that some users may find a bit more readable.

    :param target: for example a function, a class... or a string representing a function, a class...
    :return:
    """
    return case_tags(target)


test_target.__test__ = False  # disable this function in pytest (otherwise name starts with 'test' > it will appear)


@function_decorator
def cases_generator(names=None,       # type: Union[str, Callable[[Any], str], Iterable[str]]
                    lru_cache=False,  # type: bool,
                    case_func=DECORATED,
                    **param_ranges    # type: Iterable[Any]
                    ):
    """
    Decorator to declare a case function as being a cases generator. `param_ranges` should be a named list of parameter
    ranges to explore to generate the cases.

    The decorator will use `itertools.product` to create a cartesian product of the named parameter ranges, and create
    a case for each combination. When the case function will be called for a given combination, the corresponding
    parameters will be passed to the decorated function.

    >>> @cases_generator("test with i={i}", i=range(10))
    >>> def case_10_times(i):
    >>>     ''' Generates 10 cases '''
    >>>     ins = dict(a=i, b=i+1)
    >>>     outs = i+1, i+2
    >>>     return ins, outs, None

    :param names: a name template, that will be transformed into the case name using
        `names.format(**params)` for each case, where `params` is the dictionary of parameter values for this
        generated case. Alternately a callable returning a string can be provided, in which case
        `names(**params)` will be used. Finally an explicit list of names can be provided, in which case it should have
        the correct length (an error will be raised otherwise).
    :param lru_cache: a boolean (default False) indicating if the generated cases should be cached. This is identical
        to decorating the function with an additional `@lru_cache(maxsize=n)` where n is the total number of generated
        cases.
    :param param_ranges: named parameters and for each of them the list of values to be used to generate cases. For
        each combination of values (a cartesian product is made) the parameters will be passed to the underlying
        function so they should have names the underlying function can handle.
    :return:
    """
    kwarg_values = list(product(*param_ranges.values()))
    setattr(case_func, _GENERATOR_FIELD, (names, param_ranges.keys(), kwarg_values))
    if lru_cache:
        nb_cases = len(kwarg_values)
        # decorate the function with the appropriate lru cache size
        case_func = lru(maxsize=nb_cases)(case_func)

    return case_func
