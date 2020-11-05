# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_with_cases, fixture, parametrize


@fixture(scope='session')
def db():
    """
    Returns a database.

    Args:
    """
    return {0: 'louise', 1: 'bob'}


def user_bob(db):
    """
    Return a bobobuf for a database.

    Args:
        db: (todo): write your description
    """
    return db[1]


@parametrize(id=range(2))
def user_from_db(db, id):
    """
    Get a database from a database.

    Args:
        db: (todo): write your description
        id: (int): write your description
    """
    return db[id]


@parametrize_with_cases("a", cases='.', prefix='user_')
def test_users(a, db, request):
    """
    Test for all users.

    Args:
        a: (todo): write your description
        db: (todo): write your description
        request: (todo): write your description
    """
    print("this is test %r" % request.node.nodeid)
    assert a in db.values()


def test_users_synthesis(request, db):
    """
    Test for test test users.

    Args:
        request: (todo): write your description
        db: (todo): write your description
    """
    results_dct = get_session_synthesis_dct(request, filter=test_users, test_id_format='function')
    assert list(results_dct) == [
        'test_users[a_is_bob]',
        'test_users[a_is_from_db-id=0]',
        'test_users[a_is_from_db-id=1]'
    ]
