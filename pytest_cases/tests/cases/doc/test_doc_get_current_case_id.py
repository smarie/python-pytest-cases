from pytest_cases import parametrize_with_cases, fixture, get_current_case_id


def data_b():
    return 1, 2


@parametrize_with_cases("data", cases=data_b, prefix="data_")
def test_lazy_val_case(data, request):
    assert get_current_case_id(request, "data") == "b"


@parametrize_with_cases("data,data2", cases=data_b, prefix="data_")
def test_lazy_val_case_2_args(data, data2, request):
    assert get_current_case_id(request, ["data", "data2"]) == "b"


@fixture
def a():
    return


def data_a(a):
    return 1, 2


@parametrize_with_cases("data", cases=data_a, prefix="data_")
def test_fixture_case(data, request):
    assert get_current_case_id(request.node, "data") == "a"


@parametrize_with_cases("data,data2", cases=data_a, prefix="data_")
def test_fixture_case_2_args(data, data2, request):
    assert get_current_case_id(request.node, "data,data2") == "a"
