from pytest_cases import param_fixture, fixture_union

a = param_fixture("a", [1, 2])
b = param_fixture("b", [3, 4])

c = fixture_union('c', ['a', b], ids=['A', 'B'], idstyle='explicit')
d = fixture_union('d', ['a'], idstyle='compact')
e = fixture_union('e', ['a'], idstyle=None)


def test_the_ids(c, d, e):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ['test_the_ids[c_is_A-1-Ua-a]',
                                        'test_the_ids[c_is_A-2-Ua-a]',
                                        'test_the_ids[c_is_B-3-Ua-1-a]',
                                        'test_the_ids[c_is_B-3-Ua-2-a]',
                                        'test_the_ids[c_is_B-4-Ua-1-a]',
                                        'test_the_ids[c_is_B-4-Ua-2-a]',
                                        ]
