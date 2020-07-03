from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_with_cases, fixture, parametrize


@fixture(scope='session')
def db(request):
    return {0: 'zero', 1: (2, 3)}


def case_fix(db):
    return db[0]


@parametrize(key=[0, 1])
def case_fix_param(db, key):
    return db[key]


@parametrize_with_cases("a", cases='.')
def test_foo_fixtures(a, db, request):
    print("this is test %r" % request.node.nodeid)
    assert a in db.values()


def test_foo_fixtures_synthesis(request, db):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_fixtures, test_id_format='function')
    assert list(results_dct) == [
        'test_foo_fixtures[a_is_fix]',
        'test_foo_fixtures[a_is_fix_param-key=0]',
        'test_foo_fixtures[a_is_fix_param-key=1]'
    ]
