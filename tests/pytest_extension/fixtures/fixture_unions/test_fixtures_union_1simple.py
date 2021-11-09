# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import param_fixture, fixture_union, fixture

a = param_fixture('a', ['x', 'y'])


@fixture(params=[1, 2])
def b(request):
    # make sure that if this is called, then it is for a good reason
    assert request.param in [1, 2]
    return request.param


c = fixture_union('c', [a, b], idstyle="explicit")


def test_fixture_union(c, a):
    print(c, a)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_fixture_union[c/a-x]",
                                        "test_fixture_union[c/a-y]",
                                        "test_fixture_union[c/b-1-x]",
                                        "test_fixture_union[c/b-1-y]",
                                        "test_fixture_union[c/b-2-x]",
                                        "test_fixture_union[c/b-2-y]"]
