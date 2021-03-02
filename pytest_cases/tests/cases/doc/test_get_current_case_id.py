from pytest_cases import parametrize_with_cases, fixture, get_current_case_id


def data_b():
    return 1


@parametrize_with_cases("data", cases=data_b, prefix="data_")
def test_lazy_val_case(data, request):
    assert get_current_case_id(request, "data") == "b"


@fixture
def a():
    return


def data_a(a):
    return 1


@parametrize_with_cases("data", cases=data_a, prefix="data_")
def test_fixture_case(data, request):
    assert get_current_case_id(request.node, "data") == "a"
