# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import case


@case(marks=pytest.mark.skipif(True, reason="hello"))
def two_positive_ints():
    """ Inputs are two positive integers """
    return 1, 2


class CasesFoo:
    @classmethod
    def case_toto(cls):
        return 0, 0

    @staticmethod
    def case_foo():
        return 0, 0

    @case(id="hello")
    def case_blah(self):
        """a blah"""
        return 0, 0

    @pytest.mark.skip
    def case_skipped(self):
        """skipped case"""
        return 0

    def case_two_negative_ints(self):
        """ Inputs are two negative integers """
        return -1, -2


@pytest.mark.skip
def case_three_negative_ints():
    """ Inputs are three negative integers """
    return -1, -2, -6


def case_two_negative_ints():
    """ Inputs are two negative integers """
    return -1, -2
