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
    return CaseFilter(lambda case: tag_name in CaseInfo.get_from(case).tags)


def has_prefix(prefix):
    return CaseFilter(lambda case: case.__name__.startswith(prefix))


def has_suffix(suffix):
    return CaseFilter(lambda case: case.__name__.endswith(suffix))


def match_regex(regex):
    return CaseFilter(lambda case: re.match(regex, case.__name__))
