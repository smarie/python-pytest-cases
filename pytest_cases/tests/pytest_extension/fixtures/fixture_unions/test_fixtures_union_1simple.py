# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import param_fixture, fixture_union, pytest_fixture_plus

a = param_fixture('a', ['x', 'y'])


@pytest_fixture_plus(params=[1, 2])
def b(request):
    """
    Return a list of a request.

    Args:
        request: (todo): write your description
    """
    # make sure that if this is called, then it is for a good reason
    assert request.param in [1, 2]
    return request.param


c = fixture_union('c', [a, b])


def test_fixture_union(c, a):
    """
    Test if a union of two - fixture.

    Args:
        c: (todo): write your description
        a: (todo): write your description
    """
    print(c, a)


def test_synthesis(module_results_dct):
    """
    Test for the test results to test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ["test_fixture_union[c_is_a-x]",
                                        "test_fixture_union[c_is_a-y]",
                                        "test_fixture_union[c_is_b-1-x]",
                                        "test_fixture_union[c_is_b-1-y]",
                                        "test_fixture_union[c_is_b-2-x]",
                                        "test_fixture_union[c_is_b-2-y]"]
