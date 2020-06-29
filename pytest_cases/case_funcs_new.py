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

    @classmethod
    def get_from(cls, case_func, create=False):
        """return the CaseInfo associated with case_fun ; create it and attach it if needed and required"""
        case_info = getattr(case_func, CASE_FIELD, None)
        if case_info is None and create:
            case_info = CaseInfo()
            case_info.attach_to(case_func)
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
                          has_tag=None,  # type: Any
                          filter=None    # type: Callable[[Iterable[Any]], bool]  # noqa
                          ):
        """
        Returns True if the case function with this case_info is selected by the query

        :param has_tag:
        :param filter: a callable
        :return:
        """
        selected = True  # by default select the case, then AND the conditions
        if has_tag is not None:
            selected = selected and (has_tag in self.tags)
        if filter is not None:
            selected = selected and filter(self.tags)

        return selected

    @classmethod
    def copy_info(cls, from_case_func, to_case_func):
        case_info = cls.get_from(from_case_func)
        if case_info is not None:
            cp = copy(case_info)
            cp.attach_to(to_case_func)


def matches_tag_query(case_fun,
                      has_tag=None,  # type: Any
                      filter=None    # type: Callable[[Iterable[Any]], bool]  # noqa
                      ):
    """
    Returns True if the case function is selected by the query

    :param case_fun:
    :param has_tag:
    :param filter:
    :return:
    """
    # no query = match
    if has_tag is None and filter is None:
        return True

    # query = first get info
    case_info = CaseInfo.get_from(case_fun)
    if not case_info:
        # no tags: do the test on an empty case info
        return CaseInfo().matches_tag_query(has_tag, filter)
    else:
        return case_info.matches_tag_query(has_tag, filter)


@function_decorator
def case(id=None,             # type: str  # noqa
         tags=None,           # type: Union[Any, Iterable[Any]]
         # lru_cache=False,     # type: bool
         marks=(),            # type: Union[MarkDecorator, Iterable[MarkDecorator]]
         case_func=DECORATED  # noqa
         ):
    """

    :param id: the custom pytest id that should be used when this case is active. Replaces the deprecated `@case_name`
    :param tags: custom tags to be used for filtering. Replaces the deprecated `@case_tags`
    :param lru_cache:
    :param marks:
    :return:
    """
    # if lru_cache:
    #     nb_cases = 1  # TODO change when fixture dependencies are taken into account. What about creating a dedicated independent cache decorator pytest goodie ?
    #     # decorate the function with the appropriate lru cache size
    #     case_func = lru(maxsize=nb_cases)(case_func)

    case_info = CaseInfo(id, marks, tags)
    case_info.attach_to(case_func)
    return case_func


CASE_PREFIX_CLS = 'Case'
"""Prefix used by default to identify case classes"""

CASE_PREFIX_FUN = 'case_'
"""Prefix used by default to identify case functions within a module"""


def is_case_class(cls):
    return safe_isclass(cls) and cls.__name__.startswith(CASE_PREFIX_CLS)


def is_case_function(f, enforce_prefix=True):
    if not callable(f):
        return False
    elif safe_isclass(f):
        return False
    elif hasattr(f, CASE_FIELD):
        return True
    else:
        return f.__name__.startswith(CASE_PREFIX_FUN) if enforce_prefix else True
