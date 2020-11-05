# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_harvest import get_session_synthesis_dct

from pytest_cases.common_pytest_marks import has_pytest_param
from pytest_cases import parametrize_with_cases, case, parametrize


def data_a():
    """
    Èi̇·åıĸåĩº¿

    Args:
    """
    return 'a'


@parametrize("hello", [True, False])
def data_b(hello):
    """
    Return the data b.

    Args:
        hello: (bool): write your description
    """
    return "hello" if hello else "world"


def case_c():
    """
    Return a dict with the case - insensitive name.

    Args:
    """
    return dict(name="hi i'm not used")


def user_bob():
    """
    Return a user - like object of the user - specified.

    Args:
    """
    return "bob"


@parametrize_with_cases("data", cases='.', prefix="data_")
@parametrize_with_cases("user", cases='.', prefix="user_")
def test_with_data(data, user):
    """
    Set test data.

    Args:
        data: (array): write your description
        user: (todo): write your description
    """
    assert data in ('a', "hello", "world")
    assert user == 'bob'


def test_with_data_synthesis(request):
    """
    Test for test test test test test data test.

    Args:
        request: (todo): write your description
    """
    results_dct = get_session_synthesis_dct(request, filter=test_with_data, test_id_format='function')
    # if has_pytest_param:
    assert list(results_dct) == [
        'test_with_data[bob-a]',
        'test_with_data[bob-b-True]',
        'test_with_data[bob-b-False]'
    ]
    # else:
    #     assert list(results_dct) == [
    #         'test_with_data[a-bob]',
    #         'test_with_data[b-True-bob]',
    #         'test_with_data[b-False-bob]'
    #     ]


class Foo:
    def case_two_positive_ints(self):
        """
        Return the number of two integers.

        Args:
            self: (todo): write your description
        """
        return 1, 2

    @case(tags='foo')
    def case_one_positive_int(self):
        """
        Returns : class : ~.

        Args:
            self: (todo): write your description
        """
        return 1


@parametrize_with_cases("a", cases=Foo, has_tag='foo')
def test_foo(a):
    """
    Åīľ´

    Args:
        a: (todo): write your description
    """
    assert a > 0


def test_foo_fixtures_synthesis(request):
    """
    Shows test test test case.

    Args:
        request: (todo): write your description
    """
    results_dct = get_session_synthesis_dct(request, filter=test_foo, test_id_format='function')
    assert list(results_dct) == [
        'test_foo[one_positive_int]',
    ]
