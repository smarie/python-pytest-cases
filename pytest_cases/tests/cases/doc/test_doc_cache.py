# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize, parametrize_with_cases, fixture


already_read = set()


@parametrize(a=range(2))
def case_dummy(a):
    """
    Case - only global dummy dummy object.

    Args:
        a: (todo): write your description
    """
    global already_read
    if a in already_read:
        raise ValueError()
    else:
        already_read.add(a)
        return a


@fixture(scope='session')
@parametrize_with_cases("a", cases='.')
def cached_a(a):
    """
    Cached version of the first n * a.

    Args:
        a: (todo): write your description
    """
    return a


@parametrize(d=range(2))
def test_caching(cached_a, d):
    """
    Test if a set of the same as a test.

    Args:
        cached_a: (bool): write your description
        d: (todo): write your description
    """
    assert d < 2
    assert 0 <= cached_a <= 1


def test_synthesis(module_results_dct):
    """
    Test if a module_results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == [
        'test_caching[dummy-a=0-d=0]',
        'test_caching[dummy-a=0-d=1]',
        'test_caching[dummy-a=1-d=0]',
        'test_caching[dummy-a=1-d=1]'
    ]
