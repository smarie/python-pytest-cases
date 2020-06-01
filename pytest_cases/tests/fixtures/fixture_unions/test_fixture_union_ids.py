from pytest_cases import param_fixture, fixture_union

a = param_fixture("a", [1, 2])
b = param_fixture("b", [3, 4])

c = fixture_union('c', ['a', b], ids=['c=A', 'c=B'])
d = fixture_union('d', ['a'], idstyle='compact')
e = fixture_union('e', ['a'], idstyle=None)
f = fixture_union('f', ['a'])


def test_the_ids(c, d, e, f):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_the_ids[c=A-1-Ua-a-f_is_a]',
                                        'test_the_ids[c=A-2-Ua-a-f_is_a]',
                                        'test_the_ids[c=B-3-Ua-1-a-f_is_a]',
                                        'test_the_ids[c=B-3-Ua-2-a-f_is_a]',
                                        'test_the_ids[c=B-4-Ua-1-a-f_is_a]',
                                        'test_the_ids[c=B-4-Ua-2-a-f_is_a]',
                                        ]
