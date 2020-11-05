# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import param_fixture, fixture_union

a = param_fixture("a", [1, 2])
b = param_fixture("b", [3, 4])

c = fixture_union('c', ['a', b], ids=['c=A', 'c=B'])
d = fixture_union('d', ['a'], idstyle='compact')
e = fixture_union('e', ['a'], idstyle=None)
f = fixture_union('f', ['a'])


def test_the_ids(c, d, e, f):
    """
    Test if a list of ids

    Args:
        c: (todo): write your description
        d: (todo): write your description
        e: (todo): write your description
        f: (todo): write your description
    """
    pass


def test_synthesis(module_results_dct):
    """
    Test if the test results to test results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert list(module_results_dct) == ['test_the_ids[c=A-1-Ua-a-f_is_a]',
                                        'test_the_ids[c=A-2-Ua-a-f_is_a]',
                                        'test_the_ids[c=B-3-Ua-1-a-f_is_a]',
                                        'test_the_ids[c=B-3-Ua-2-a-f_is_a]',
                                        'test_the_ids[c=B-4-Ua-1-a-f_is_a]',
                                        'test_the_ids[c=B-4-Ua-2-a-f_is_a]',
                                        ]
