from collections import namedtuple

from decopatch import function_decorator, DECORATED

try:  # python 3.2+
    from functools import lru_cache as lru
except ImportError:
    from functools32 import lru_cache as lru  # noqa

try:  # python 3.5+
    from typing import Type, Callable, Union, Optional, Any, Tuple, Dict, Iterable
except:  # noqa
    pass

from .common_pytest import safe_isclass

# ---------- tags -----------
CASE_TAGS_FIELD = '__case_tags__'


def _add_tags(case_func,   # type: Callable
              tags         # type: Iterable[Any]
              ):
    """Adds the given tags to the given case function"""
    existing_tags = getattr(case_func, CASE_TAGS_FIELD, None)
    if existing_tags is None:
        # there are no tags yet. Use the provided ones, converted to list
        setattr(case_func, CASE_TAGS_FIELD, list(tags))
    else:
        # there are some tags already, let's try to add the new to the existing list
        setattr(case_func, CASE_TAGS_FIELD, existing_tags + tags)


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
    #  - with the optional filter/tag
    _tags = getattr(case_fun, CASE_TAGS_FIELD, ())

    selected = True  # by default select the case, then AND the conditions
    if has_tag is not None:
        selected = selected and (has_tag in _tags)
    if filter is not None:
        selected = selected and filter(_tags)
    return selected


CaseInfo = namedtuple('CaseInfo', ('id', 'marks'))


CASE_FIELD = '_pytestcase'


def get_case_info(case_fun):
    # type: (...) -> CaseInfo
    return getattr(case_fun, CASE_FIELD, None)


@function_decorator
def case(id=None,             # type: str  # noqa
         target=None,         # type: Any
         tags=None,           # type: Iterable[Any]
         lru_cache=False,     # type: bool
         marks=(),            # type: Union[MarkDecorator, Iterable[MarkDecorator]]
         case_func=DECORATED  # noqa
         ):
    """

    :param id: the custom pytest id that should be used when this case is active. Replaces the deprecated `@case_name`
    :param target: the custom target associated with this case. Replaces the deprecated `@test_target`
    :param tags: custom tags to be used for filtering. Replaces the deprecated `@case_tags`
    :param lru_cache:
    :param marks:
    :return:
    """
    if target:
        _add_tags(case_func, [target])

    if tags:
        _add_tags(case_func, tuple(tags))

    if not target and not tags:
        # add no tags but that is a hint that this is a case
        _add_tags(case_func, ())

    if lru_cache:
        nb_cases = 1  # TODO change when fixture dependencies are taken into account. What about creating a dedicated independent cache decorator pytest goodie ?
        # decorate the function with the appropriate lru cache size
        case_func = lru(maxsize=nb_cases)(case_func)

    setattr(case_func, CASE_FIELD, CaseInfo(id, marks))
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


def copy_case_infos(from_case, to_case):
    case_info = get_case_info(from_case)
    if case_info is not None:
        setattr(to_case, CASE_FIELD, case_info)

    # not needed: the tags are only used when case is collected, not more.
    # existing_tags = getattr(from_case, CASE_TAGS_FIELD, None)
    # if existing_tags is None:
    #     # there are no tags yet. Use the provided ones, converted to list
    #     setattr(to_case, CASE_TAGS_FIELD, existing_tags)
