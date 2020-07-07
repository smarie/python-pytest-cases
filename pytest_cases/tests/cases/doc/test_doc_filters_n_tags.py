from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_with_cases, case, parametrize


def data_a():
    return 'a'


@parametrize("hello", [True, False])
def data_b(hello):
    return "hello" if hello else "world"


def case_c():
    return dict(name="hi i'm not used")


class Foo:
    def case_two_positive_ints(self):
        return 1, 2

    @case(tags='foo')
    def case_one_positive_int(self):
        return 1


@parametrize_with_cases("data", cases='.', prefix="data_")
def test_with_data(data):
    assert data in ('a', "hello", "world")


def test_with_data_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_with_data, test_id_format='function')
    assert list(results_dct) == [
        'test_with_data[a]',
        'test_with_data[b-True]',
        'test_with_data[b-False]'
    ]


@parametrize_with_cases("a", cases=Foo, has_tag='foo')
def test_foo(a):
    assert a > 0


def test_foo_fixtures_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo, test_id_format='function')
    assert list(results_dct) == [
        'test_foo[one_positive_int]',
    ]
