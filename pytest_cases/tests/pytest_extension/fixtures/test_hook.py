# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import unpack_fixture, fixture, param_fixture, param_fixtures, fixture_union, parametrize, \
    fixture_ref


f_list = []


def my_hook(fixture_fun):
    print(fixture_fun)
    f_list.append(fixture_fun.__name__)
    return fixture_fun


@fixture(hook=my_hook)
def foo():
    return 2, 1


o, p = unpack_fixture('o,p', foo, hook=my_hook)


p1 = param_fixture("p1", [1, 2], hook=my_hook)

p2, p3 = param_fixtures("p2,p3", [(3, 4)], hook=my_hook)

u = fixture_union("u", (o, p), hook=my_hook)


@parametrize("arg", [fixture_ref(u),
                          fixture_ref(p1)])
def test_a(arg, p2, p3):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_a[u-/o-3-4]',
        'test_a[u-/p-3-4]',
        'test_a[p1-1-3-4]',
        'test_a[p1-2-3-4]'
    ]
    assert f_list == ['foo', 'o', 'p', 'p1', 'p2_p3__param_fixtures_root', 'p2', 'p3', 'u']
