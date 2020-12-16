from pytest_harvest import get_session_synthesis_dct

from pytest_cases.common_pytest_marks import has_pytest_param
from pytest_cases import parametrize_with_cases, AUTO

from .example import foo


@parametrize_with_cases("a,b")
def test_foo_alternate_cases_file_and_two_marked_skip(a, b):
    assert isinstance(foo(a, b), tuple)


@parametrize_with_cases("a,b", cases=AUTO)
def test_foo_alternate_cases_file_and_two_marked_skip(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_alternate_cases_file_and_two_marked_skip_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_alternate_cases_file_and_two_marked_skip,
                                            test_id_format='function')
    if has_pytest_param:
        assert list(results_dct) == [
            'test_foo_alternate_cases_file_and_two_marked_skip[toto]',
            'test_foo_alternate_cases_file_and_two_marked_skip[foo]',
            'test_foo_alternate_cases_file_and_two_marked_skip[hello]',
            'test_foo_alternate_cases_file_and_two_marked_skip[two_negative_ints0]',
            'test_foo_alternate_cases_file_and_two_marked_skip[two_negative_ints1]'
        ]
    else:
        assert list(results_dct) == [
            'test_foo_alternate_cases_file_and_two_marked_skip[0toto[0]-toto[1]]',
            'test_foo_alternate_cases_file_and_two_marked_skip[1foo[0]-foo[1]]',
            'test_foo_alternate_cases_file_and_two_marked_skip[2hello[0]-hello[1]]',
            'test_foo_alternate_cases_file_and_two_marked_skip[4two_negative_ints[0]-two_negative_ints[1]]',
            'test_foo_alternate_cases_file_and_two_marked_skip[6two_negative_ints[0]-two_negative_ints[1]]'
        ]
