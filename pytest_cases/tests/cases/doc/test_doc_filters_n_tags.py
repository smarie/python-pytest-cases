# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_with_cases, case, parametrize


@pytest.mark.parametrize("data", ["a", "b"])
@pytest.mark.parametrize("user", ["bob"])
def test_default_pytest_order(data, user):
    pass


def datnop_a():
    return 'a'


def datnop_b():
    return 'b'


def data_a():
    return 'a'


@parametrize("hello", [True, False])
def data_b(hello):
    return "hello" if hello else "world"


def case_c():
    return dict(name="hi i'm not used")


def user_bob():
    return "bob"


@parametrize_with_cases("data", cases='.', prefix="datnop_")
@parametrize_with_cases("user", cases='.', prefix="user_")
def test_with_data_non_param(data, user):
    assert data in ('a', "b")
    assert user == 'bob'


@parametrize_with_cases("data", cases='.', prefix="data_")
@parametrize_with_cases("user", cases='.', prefix="user_")
def test_with_data_param(data, user):
    assert data in ('a', "hello", "world")
    assert user == 'bob'


def test_with_data_synthesis(module_results_dct):
    # if has_pytest_param:
    assert list(module_results_dct) == [
        # pytest parametrize
        'test_default_pytest_order[bob-a]',
        'test_default_pytest_order[bob-b]',
        # if cases are not parametrized themselves, they are not turned into fixtures so the order remains
        'test_with_data_non_param[bob-a]',
        'test_with_data_non_param[bob-b]',
        # if cases are parametrized, they are turned into fixtures right now so the order changes
        'test_with_data_param[a-bob]',
        'test_with_data_param[b-True-bob]',
        'test_with_data_param[b-False-bob]'
    ]
    # else:
    #     assert list(results_dct) == [
    #         'test_with_data[a-bob]',
    #         'test_with_data[b-True-bob]',
    #         'test_with_data[b-False-bob]'
    #     ]


class Foo:
    def case_two_positive_ints(self):
        return 1, 2

    @case(tags='foo')
    def case_one_positive_int(self):
        return 1


@parametrize_with_cases("a", cases=Foo, has_tag='foo')
def test_foo(a):
    assert a > 0


def test_foo_fixtures_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo, test_id_format='function')
    assert list(results_dct) == [
        'test_foo[one_positive_int]',
    ]
