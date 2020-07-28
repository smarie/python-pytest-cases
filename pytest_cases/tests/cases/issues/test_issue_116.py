from pytest_cases import fixture


@fixture(autouse=True)
def a():
    return


def test_issue116(request):
    request._pyfuncitem._fixtureinfo.names_closure.remove('a')
