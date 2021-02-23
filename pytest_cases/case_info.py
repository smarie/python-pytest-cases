from copy import copy

try:  # python 3.5+
    from typing import Type, Callable, Union, Optional, Any, Tuple, Dict, Iterable, List, Set
except ImportError:
    pass
from .common_mini_six import string_types


CASE_FIELD = '_pytestcase'


class CaseInfo(object):
    """
    Contains all information available about a case.
    It is attached to a case function as an attribute
    """
    __slots__ = ('id', 'marks', 'tags')

    def __init__(self,
                 id=None,   # type: str
                 marks=(),  # type: Tuple[MarkDecorator, ...]
                 tags=()    # type: Tuple[Any]
                 ):
        self.id = id
        self.marks = marks
        self.tags = ()
        self.add_tags(tags)

    def __repr__(self):
        return "_CaseInfo(id=%r,marks=%r,tags=%r)" % (self.id, self.marks, self.tags)

    @classmethod
    def get_from(cls,
                 case_func,               # type: Callable
                 create_if_missing=False  # type: bool
                 ):
        """ Return the _CaseInfo associated with case_fun or None

        :param case_func:
        :param create_if_missing: if no case information is present on the function, by default None is returned. If
            this flag is set to True, a new _CaseInfo will be created and attached on the function, and returned.
        """
        ci = getattr(case_func, CASE_FIELD, None)
        if ci is None and create_if_missing:
            ci = cls()
            ci.attach_to(case_func)
        return ci

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
        return _tags_match_query(self.tags, has_tag)

    @classmethod
    def copy_info(cls,
                  from_case_func,
                  to_case_func):
        case_info = cls.get_from(from_case_func)
        if case_info is not None:
            # there is something to copy: do it
            cp = copy(case_info)
            cp.attach_to(to_case_func)


def _tags_match_query(tags,    # type: Iterable[str]
                      has_tag  # type: Optional[Union[str, Iterable[str]]]
                      ):
    """Internal routine to determine is all tags in `has_tag` are persent in `tags`
    Note that `has_tag` can be a single tag, or none
    """
    if has_tag is None:
        return True

    if not isinstance(has_tag, (tuple, list, set)):
        has_tag = (has_tag,)

    return all(t in tags for t in has_tag)
