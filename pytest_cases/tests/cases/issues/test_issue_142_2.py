from pytest_cases import parametrize_with_cases, lazy_value, parametrize
from pytest_cases.common_pytest_marks import has_pytest_param


def case_dumb():
    return 1, 2


@parametrize("a,b", [(1, object()), lazy_value(case_dumb)])
def test_foo(a, b):
    pass


@parametrize_with_cases('a,b', cases='.')
def test_tuples_no_id(a, b):
    assert True


# --------- now we do the same with an id generator


@parametrize("a,b", [(1, object()), lazy_value(case_dumb)], ids=["hello", "world"])
def test_foo2(a, b):
    pass


def generate_id(o):
    return "hello"


@parametrize_with_cases('a,b', cases='.', ids=generate_id)
def test_tuples(a, b):
    assert True


def test_synthesis(module_results_dct):
    if has_pytest_param:
        assert list(module_results_dct) == [
            "test_foo[1-b0]",
            "test_foo[case_dumb]",
            'test_tuples_no_id[dumb]',
            "test_foo2[hello]",
            "test_foo2[world]",
            'test_tuples[hello]',
        ]
    else:
        # no pytest.param exists in this old pytest so the ids can not all be fixed
        assert list(module_results_dct) == [
            "test_foo[1-b0]",
            "test_foo[case_dumb[0]-case_dumb[1]]",
            'test_tuples_no_id[dumb[0]-dumb[1]]',
            "test_foo2[hello]",
            "test_foo2[world]",
            'test_tuples[hello]',
        ]
