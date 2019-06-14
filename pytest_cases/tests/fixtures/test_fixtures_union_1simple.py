from pytest_cases import param_fixture, fixture_union, pytest_fixture_plus

a = param_fixture('a', ['x', 'y'])


@pytest_fixture_plus(params=[1, 2])
def b(request):
    # make sure that if this is called, then it is for a good reason
    assert request.param in [1, 2]
    return request.param


c = fixture_union('c', [a, b])


def test_fixture_union(c, a):
    print(c, a)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_fixture_union[c_is_a-x]",
                                        "test_fixture_union[c_is_a-y]",
                                        "test_fixture_union[c_is_b-1-x]",
                                        "test_fixture_union[c_is_b-1-y]",
                                        "test_fixture_union[c_is_b-2-x]",
                                        "test_fixture_union[c_is_b-2-y]"]
