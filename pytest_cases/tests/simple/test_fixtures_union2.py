from pytest_cases import param_fixture, fixture_union


a = param_fixture('a', ['x', 'y'])
b = param_fixture('b', [1, 2])
c = fixture_union('c', a, b)


def test_fixture_union(c, a):
    print(c, a)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_fixture_union[x]",
                                        "test_fixture_union[y]",
                                        "test_fixture_union[1-x]",
                                        "test_fixture_union[1-y]",
                                        "test_fixture_union[2-x]",
                                        "test_fixture_union[2-y]"]
