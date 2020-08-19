from copy import copy

from decopatch import function_decorator, DECORATED

# try:  # python 3.2+
#     from functools import lru_cache as lru
# except ImportError:
#     from functools32 import lru_cache as lru  # noqa

try:  # python 3.5+
    from typing import Type, Callable, Union, Optional, Any, Tuple, Dict, Iterable, List, Set
except ImportError:
    pass

from .common_mini_six import string_types
from .common_pytest import safe_isclass


CASE_FIELD = '_pytestcase'


class CaseInfo(object):
    """
    Contains all information available about a case.
    It is attached to a case function as an attribute
    """
    __slots__ = ('id', 'marks', 'tags')

    def __init__(self,
                 id=None,   # type: str
                 marks=(),  # type: Tuple[MarkDecorator]
                 tags=()    # type: Tuple[Any]
                 ):
        self.id = id
        self.marks = marks
        self.tags = ()
        self.add_tags(tags)

    def __repr__(self):
        return "CaseInfo(id=%r,marks=%r,tags=%r)" % (self.id, self.marks, self.tags)

    @classmethod
    def get_from(cls, case_func, create=False, prefix_for_ids='case_'):
        """
        Returns the CaseInfo associated with case_fun ; creates it and attaches it if needed and required.
        If not present, a case id is automatically created from the function name based on the collection prefix.

        :param case_func:
        :param create:
        :param prefix_for_ids:
        :return:
        """
        case_info = getattr(case_func, CASE_FIELD, None)

        if create:
            if case_info is None:
                case_info = CaseInfo()
                case_info.attach_to(case_func)

            if case_info.id is None:
                # default test id from function name
                if case_func.__name__.startswith(prefix_for_ids):
                    case_info.id = case_func.__name__[len(prefix_for_ids):]
                else:
                    case_info.id = case_func.__name__

        return case_info

    def attach_to(self,
                  case_func  # type: Callable
                  ):
        """attach this case_info to the given case function"""
        setattr(case_func, CASE_FIELD, self)

    def add_tags(self,
                 tags  # type: Union[Any, Union[List, Set, Tuple]]
                 ):
        """add the given tag or tags"""
        if tags:
            if isinstance(tags, string_types) or not isinstance(tags, (set, list, tuple)):
                # a single tag, create a tuple around it
                tags = (tags,)

            self.tags += tuple(tags)

    def matches_tag_query(self,
                          has_tag=None,  # type: Union[str, Iterable[str]]
                          ):
        """
        Returns True if the case function with this case_info is selected by the query

        :param has_tag:
        :return:
        """
        if has_tag is None:
            return True

        if not isinstance(has_tag, (tuple, list, set)):
            has_tag = (has_tag,)

        return all(t in self.tags for t in has_tag)

    @classmethod
    def copy_info(cls, from_case_func, to_case_func):
        case_info = cls.get_from(from_case_func)
        if case_info is not None:
            cp = copy(case_info)
            cp.attach_to(to_case_func)


def matches_tag_query(case_fun,
                      has_tag=None,  # type: Union[str, Iterable[str]]
                      filter=None,   # type: Union[Callable[[Iterable[Any]], bool], Iterable[Callable[[Iterable[Any]], bool]]]  # noqa
                      ):
    """
    Returns True if the case function is selected by the query:

     - if `has_tag` contains one or several tags, they should ALL be present in the tags
       set on `case_fun` (`case_fun._pytestcase.tags`)

     - if `filter` contains one or several filter callables, they are all called in sequence and the
       case_fun is only selected if ALL of them return a True truth value

    :param case_fun:
    :param has_tag:
    :param filter:
    :return: True if the case_fun is selected by the query.
    """
    selected = True

    # query on tags
    if has_tag is not None:
        selected = selected and CaseInfo.get_from(case_fun).matches_tag_query(has_tag)

    # filter function
    if filter is not None:
        if not isinstance(filter, (tuple, set, list)):
            filter = (filter,)

        for _filter in filter:
            # break if already unselected
            if not selected:
                return selected

            # try next filter
            try:
                res = _filter(case_fun)
                # keep this in the try catch in case there is an issue with the truth value of result
                selected = selected and res
            except:  # noqa
                # any error leads to a no-match
                selected = False

    return selected


@function_decorator
def case(id=None,             # type: str  # noqa
         tags=None,           # type: Union[Any, Iterable[Any]]
         marks=(),            # type: Union[MarkDecorator, Iterable[MarkDecorator]]
         case_func=DECORATED  # noqa
         ):
    """
    Optional decorator for case functions so as to customize some information.

    ```python
    @case(id='hey')
    def case_hi():
        return 1
    ```

    :param id: the custom pytest id that should be used when this case is active. Replaces the deprecated `@case_name`
        decorator from v1. If no id is provided, the id is generated from case functions by removing their prefix,
        see `@parametrize_with_cases(prefix='case_')`.
    :param tags: custom tags to be used for filtering in `@parametrize_with_cases(has_tags)`. Replaces the deprecated
        `@case_tags` and `@target` decorators.
    :param marks: optional pytest marks to add on the case. Note that decorating the function directly with the mark
        also works, and if marks are provided in both places they are merged.
    :return:
    """
    case_info = CaseInfo(id, marks, tags)
    case_info.attach_to(case_func)
    return case_func


CASE_PREFIX_CLS = 'Case'
"""Prefix used by default to identify case classes"""

CASE_PREFIX_FUN = 'case_'
"""Prefix used by default to identify case functions within a module"""


def is_case_class(cls, case_marker_in_name=CASE_PREFIX_CLS, check_name=True):
    """
    Returns True if the given object is a class and, if `check_name=True` (default), if its name contains
    `case_marker_in_name`.

    :param cls: the object to check
    :param case_marker_in_name: the string that should be present in a class name so that it is selected. Default is
        'Case'.
    :param check_name: a boolean (default True) to enforce that the name contains the word `case_marker_in_name`.
        If False, all classes will lead to a `True` result whatever their name.
    :return: True if this is a case class
    """
    return safe_isclass(cls) and (not check_name or case_marker_in_name in cls.__name__)


def is_case_function(f, prefix=CASE_PREFIX_FUN, check_prefix=True):
    """
    Returns True if the provided object is a function or callable and, if `check_prefix=True` (default), if it starts
    with `prefix`.

    :param f:
    :param prefix:
    :param check_prefix:
    :return:
    """
    if not callable(f):
        return False
    elif safe_isclass(f):
        return False
    elif hasattr(f, '_pytestcasesgen'):
        # a function generated by us. ignore this
        return False
    else:
        return f.__name__.startswith(prefix) if check_prefix else True
