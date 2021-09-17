from pytest_cases import parametrize_with_cases, fixture, parametrize


@parametrize(nb=(1,))
def case_a(nb):
    return nb


@fixture
@parametrize_with_cases("foo", cases=case_a)
def my_fixture(foo):
    return foo


@parametrize_with_cases("data", cases=case_a)
def test_get_current_case(data, my_fixture, current_cases):

    # this is how to access the case function for a test parameter
    actual_case_id, case_fun, case_params = current_cases["data"]

    # this is how to access the case function for a fixture parameter
    fix_actual_case_id, fix_case_fun, fix_case_params = current_cases["my_fixture"]["foo"]

    # let's print everything
    print(current_cases)

    assert current_cases == {
        "data": ("a", case_a, {'nb': 1}),
        "my_fixture": {
            "foo": ("a", case_a, {'nb': 1})
        }
    }

    print((actual_case_id, case_fun))
