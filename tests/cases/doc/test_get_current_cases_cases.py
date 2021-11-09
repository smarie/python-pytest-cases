# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import case


@case(tags=("no_fix_needed",))
def case_a():
    return 1, 2


@case(tags=("no_fix_needed",))
def case_b():
    return 1, 2


@case(id="custom_id", tags=("no_fix_needed",))
def tuplecase_a():
    return 1, 2


@case(id="custom_id", tags=("needs_fixture",))
def case_a_fixture(request):
    return 1, 2


def tuplecase_a_fixture(request):
    return 1, 2
