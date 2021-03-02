import re

from .case_info import CaseInfo


class CaseFilter(object):
    """
    This class represents a case filter. You can use it in order to filter cases
    to be used by `parametrize_by_cases`.

    You can join filters with the "and" relation by using & operator and join them
    by "or" relation using | operator.
    Moreover, you can negate a filter by using ~.
    """

    def __init__(self, filter_function):
        self.filter_function = filter_function

    def __call__(self, case):
        return self.filter_function(case)

    def __and__(self, other):
        return CaseFilter(
            lambda case: self(case) and other(case)
        )

    def __rand__(self, other):
        return self & other

    def __or__(self, other):
        return CaseFilter(
            lambda case: self(case) or other(case)
        )

    def __ror__(self, other):
        return self | other

    def __invert__(self):
        return CaseFilter(
            lambda case: not self(case)
        )


def has_tag(tag_name):
    """Select cases that have the tag `tag_name`. See `@case(tags=...)` to add tags to a case."""
    return CaseFilter(lambda case: tag_name in CaseInfo.get_from(case).tags)


def id_has_prefix(prefix):
    """
    Select cases that have a case id prefix `prefix`.

    Note that this is not the prefix of the whole case function name, but the case id,
    possibly overridden with `@case(id=)`
    """
    return CaseFilter(lambda case: CaseInfo.get_from(case).id.startswith(prefix))


def id_has_suffix(suffix):
    """
    Select cases that have a case id suffix `suffix`.

    Note that this is not the suffix of the whole case function name, but the case id,
    possibly overridden with `@case(id=)`
    """
    return CaseFilter(lambda case: CaseInfo.get_from(case).id.endswith(suffix))


def id_match_regex(regex):
    """
    Select cases that have a case id matching `regex`.

    Note that this is not a match of the whole case function name, but the case id,
    possibly overridden with `@case(id=)`
    """
    return CaseFilter(lambda case: re.match(regex, CaseInfo.get_from(case).id))
