from pytest_cases import param_fixture, fixture_union

a = param_fixture('a', ['x', 'y'])
b = param_fixture('b', [1, 2])
c = fixture_union('c', [a, b])
d = fixture_union('d', [b, a])


def test_fixture_union_harder(c, a, d):
    print(c, a, d)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_fixture_union_harder[a-x-b-1]",
                                        "test_fixture_union_harder[a-x-b-2]",
                                        "test_fixture_union_harder[a-x-a]",
                                        "test_fixture_union_harder[a-y-b-1]",
                                        "test_fixture_union_harder[a-y-b-2]",
                                        "test_fixture_union_harder[a-y-a]",
                                        "test_fixture_union_harder[b-1-x-b]",
                                        "test_fixture_union_harder[b-1-x-a]",
                                        "test_fixture_union_harder[b-1-y-b]",
                                        "test_fixture_union_harder[b-1-y-a]",
                                        "test_fixture_union_harder[b-2-x-b]",
                                        "test_fixture_union_harder[b-2-x-a]",
                                        "test_fixture_union_harder[b-2-y-b]",
                                        "test_fixture_union_harder[b-2-y-a]"]
