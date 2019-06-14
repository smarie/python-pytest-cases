from pytest_cases import param_fixture, fixture_union

# basic parametrized fixtures
a = param_fixture('a', ['x', 'y'])
b = param_fixture('b', [1, 2])

# union fixtures
c = fixture_union('c', [a, b])
d = fixture_union('d', [b, a])


def test_fixture_union_harder(c, a, d):
    print(c, a, d)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_fixture_union_harder[c_is_a-x-d_is_b-1]",
                                        "test_fixture_union_harder[c_is_a-x-d_is_b-2]",
                                        "test_fixture_union_harder[c_is_a-x-d_is_a]",
                                        "test_fixture_union_harder[c_is_a-y-d_is_b-1]",
                                        "test_fixture_union_harder[c_is_a-y-d_is_b-2]",
                                        "test_fixture_union_harder[c_is_a-y-d_is_a]",
                                        "test_fixture_union_harder[c_is_b-1-x-d_is_b]",
                                        "test_fixture_union_harder[c_is_b-1-x-d_is_a]",
                                        "test_fixture_union_harder[c_is_b-1-y-d_is_b]",
                                        "test_fixture_union_harder[c_is_b-1-y-d_is_a]",
                                        "test_fixture_union_harder[c_is_b-2-x-d_is_b]",
                                        "test_fixture_union_harder[c_is_b-2-x-d_is_a]",
                                        "test_fixture_union_harder[c_is_b-2-y-d_is_b]",
                                        "test_fixture_union_harder[c_is_b-2-y-d_is_a]"]
