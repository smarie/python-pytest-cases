from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_with_cases, fixture, parametrize


@fixture(scope='session')
def db():
    return {0: 'louise', 1: 'bob'}


def user_bob(db):
    return db[1]


@parametrize(id=range(2))
def user_from_db(db, id):
    return db[id]


@parametrize_with_cases("a", cases='.', prefix='user_')
def test_users(a, db, request):
    print("this is test %r" % request.node.nodeid)
    assert a in db.values()


def test_users_synthesis(request, db):
    results_dct = get_session_synthesis_dct(request, filter=test_users, test_id_format='function')
    assert list(results_dct) == [
        'test_users[a_is_bob]',
        'test_users[a_is_from_db-id=0]',
        'test_users[a_is_from_db-id=1]'
    ]
