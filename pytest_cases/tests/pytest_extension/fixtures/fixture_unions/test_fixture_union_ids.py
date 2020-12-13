# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import param_fixture, fixture_union

a = param_fixture("a", [1, 2])
b = param_fixture("b", [3, 4])

my_explicit = fixture_union('my_explicit', ['a', b], idstyle='explicit')
my_compact = fixture_union('my_compact', ['a', b])  # , idstyle='compact' is the default now
my_none = fixture_union('my_none', ['a', b], idstyle=None)
my_custom_list = fixture_union('my_custom_list', ['a', b], ids=['c=A', 'c=B'])

def my_gen(o):
    return str(o)

my_custom_gen = fixture_union('my_custom_gen', ['a', b], ids=my_gen)


class TestA:
    def test_ids_explicit(self, my_explicit):
        pass


def test_ids_compact(my_compact):
    pass


def test_ids_none(my_none):
    pass


def test_ids_custom_list(my_custom_list):
    pass


def test_ids_custom_gen(my_custom_gen):
    pass


# def test_ids_all_mixed(my_explicit, my_compact, my_none, my_custom_list, my_custom_gen):
#     pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_ids_explicit[my_explicit/a-1]',
        'test_ids_explicit[my_explicit/a-2]',
        'test_ids_explicit[my_explicit/b-3]',
        'test_ids_explicit[my_explicit/b-4]',
        'test_ids_compact[/a-1]',
        'test_ids_compact[/a-2]',
        'test_ids_compact[/b-3]',
        'test_ids_compact[/b-4]',
        'test_ids_none[a-1]',
        'test_ids_none[a-2]',
        'test_ids_none[b-3]',
        'test_ids_none[b-4]',
        'test_ids_custom_list[c=A-1]',
        'test_ids_custom_list[c=A-2]',
        'test_ids_custom_list[c=B-3]',
        'test_ids_custom_list[c=B-4]',
        'test_ids_custom_gen[my_custom_gen/0/a-1]',
        'test_ids_custom_gen[my_custom_gen/0/a-2]',
        'test_ids_custom_gen[my_custom_gen/1/b-3]',
        'test_ids_custom_gen[my_custom_gen/1/b-4]'
    ]
